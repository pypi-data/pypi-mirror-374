from django import forms
from netbox.forms import NetBoxModelForm
from .models import Organization, ISDAS, SCIONLinkAssignment

try:
    from django.contrib.postgres.fields import ArrayField
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class TagListWidget(forms.TextInput):
    """
    Widget for entering comma-separated tags that converts to/from list
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'placeholder': 'Enter cores separated by commas (e.g., core1.example.com, core2.example.com)'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, list):
            return ', '.join(value)
        return value

    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        if value:
            # Split by comma and clean up whitespace
            return [item.strip() for item in value.split(',') if item.strip()]
        return []


class TagListField(forms.Field):
    """
    Field for handling comma-separated tags
    """
    widget = TagListWidget

    def __init__(self, **kwargs):
        kwargs.setdefault('widget', TagListWidget())
        super().__init__(**kwargs)

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return []

    def validate(self, value):
        super().validate(value)
        if value and not isinstance(value, list):
            raise forms.ValidationError('Invalid format for core list')


class OrganizationForm(NetBoxModelForm):
    class Meta:
        model = Organization
        fields = ('short_name', 'full_name', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ISDAForm(NetBoxModelForm):
    cores = TagListField(
        required=False,
        help_text="Enter core nodes separated by commas (e.g., core1.example.com, core2.example.com)",
        label="Core Nodes"
    )
    
    class Meta:
        model = ISDAS
        fields = ('isd_as', 'description', 'organization', 'cores')
        labels = {
            'isd_as': 'ISD-AS',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'organization': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert list to comma-separated string for display
        if self.instance and self.instance.pk and self.instance.cores:
            self.initial['cores'] = ', '.join(self.instance.cores)
        
        # Manually set the organization choices to avoid API lookup
        self.fields['organization'].queryset = Organization.objects.all()

    def clean_cores(self):
        cores = self.cleaned_data.get('cores', [])
        return cores if cores else []


class SCIONLinkAssignmentForm(NetBoxModelForm):
    core = forms.CharField(
        required=True,
        help_text="Select the core for this assignment",
        label="CORE",
        widget=forms.Select(choices=[])
    )

    class Meta:
        model = SCIONLinkAssignment
        fields = ('isd_as', 'core', 'interface_id', 'relationship', 'customer_name', 'customer_id', 'zendesk_ticket')
        labels = {
            'isd_as': 'ISD-AS',
            'interface_id': 'Interface ID',
            'customer_id': 'Customer ID',
            'zendesk_ticket': 'Zendesk Ticket ID',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make customer_id optional and move it after customer_name via fields order
        self.fields['customer_id'].required = False
        
        # Set up the core field widget with initial choices
        if self.instance and self.instance.pk and self.instance.isd_as:
            cores = self.instance.isd_as.cores or []
            choices = [(core, core) for core in cores]
            if choices:
                choices.insert(0, ('', '--- Select Core ---'))
            else:
                choices = [('', 'No cores available')]
        else:
            # For new instances, start with empty choices
            choices = [('', '--- Select ISD-AS first ---')]
        
        self.fields['core'].widget.choices = choices

    def clean_zendesk_ticket(self):
        ticket = self.cleaned_data.get('zendesk_ticket')
        if ticket and not ticket.isdigit():
            raise forms.ValidationError("Zendesk ticket must contain only numbers")
        return ticket

    def clean_core(self):
        core = self.cleaned_data.get('core')
        isd_as = self.cleaned_data.get('isd_as')
        
        if core and isd_as:
            # Validate that the core exists in the selected ISD-AS
            available_cores = isd_as.cores or []
            if core not in available_cores:
                available_cores_str = ', '.join(available_cores) if available_cores else 'No cores available'
                raise forms.ValidationError(
                    f"Core '{core}' is not available for ISD-AS {isd_as}. "
                    f"Available cores: {available_cores_str}"
                )
        return core
