from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField
from .models import Organization, ISDAS, SCIONLinkAssignment


class OrganizationForm(NetBoxModelForm):
    class Meta:
        model = Organization
        fields = ('short_name', 'full_name', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ISDAForm(NetBoxModelForm):
    cores = forms.CharField(
        required=False,
        help_text="Appliances are managed in the detail page",
        label="Appliances",
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = ISDAS
        fields = ('isd_as', 'appliance_type', 'description', 'organization', 'cores')
        labels = {
            'isd_as': 'ISD-AS',
            'appliance_type': 'Appliance Type',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'organization': forms.Select(),
            'appliance_type': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep cores as hidden, they'll be managed through the detail page
        if self.instance and self.instance.pk and self.instance.cores:
            # Only show cores if they actually exist and are not empty
            if isinstance(self.instance.cores, list) and self.instance.cores:
                self.initial['cores'] = ', '.join(self.instance.cores)
            else:
                self.initial['cores'] = ''
        else:
            self.initial['cores'] = ''
        
        # Manually set the organization choices to avoid API lookup
        self.fields['organization'].queryset = Organization.objects.all()

    def clean_cores(self):
        cores_str = self.cleaned_data.get('cores', '')
        if not cores_str or cores_str.strip() == '':
            return []
        # Split by comma and clean up whitespace
        cores = [core.strip() for core in cores_str.split(',') if core.strip()]
        return cores


# New form for managing appliances in the ISD-AS detail page
class CoreManagementForm(forms.Form):
    core_name = forms.CharField(
        max_length=255,
        required=True,
        help_text="Name of the appliance",
        label="Appliance Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., s01.chgtg1.ana'
        })
    )


class SCIONLinkAssignmentForm(NetBoxModelForm):
    core = forms.ChoiceField(
        required=True,
        help_text="Select the appliance for this assignment",
        label="Appliance",
        choices=[]
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
        # Make customer_id and zendesk_ticket optional
        self.fields['customer_id'].required = False
        self.fields['zendesk_ticket'].required = False
        
        # Set up the core field choices based on the selected ISD-AS
        isd_as = None
        
        # Try to get ISD-AS from instance first
        if self.instance and self.instance.pk and hasattr(self.instance, 'isd_as') and self.instance.isd_as:
            isd_as = self.instance.isd_as
        # Try to get from form data if available
        elif args and len(args) > 0 and args[0] is not None:
            form_data = args[0]
            if isinstance(form_data, dict) and 'isd_as' in form_data and form_data['isd_as']:
                try:
                    isd_as = ISDAS.objects.get(pk=form_data['isd_as'])
                except (ISDAS.DoesNotExist, ValueError, TypeError):
                    pass
        
        # Set up choices based on available cores
        if isd_as and hasattr(isd_as, 'cores'):
            cores = isd_as.cores or []
            choices = [(core, core) for core in cores]
            if choices:
                choices.insert(0, ('', '--- Select Appliance ---'))
            else:
                choices = [('', 'No appliances available')]
        else:
            # For new instances or when no ISD-AS is selected
            choices = [('', '--- Select ISD-AS first ---')]
        
        self.fields['core'].choices = choices
    
    def full_clean(self):
        # Override full_clean to update core choices before validation
        if self.data and 'isd_as' in self.data and self.data['isd_as']:
            try:
                isd_as = ISDAS.objects.get(pk=self.data['isd_as'])
                cores = isd_as.cores or []
                choices = [(core, core) for core in cores]
                if choices:
                    choices.insert(0, ('', '--- Select Appliance ---'))
                else:
                    choices = [('', 'No appliances available')]
                self.fields['core'].choices = choices
                    
            except (ISDAS.DoesNotExist, ValueError, TypeError):
                pass
        
        # Now run the normal validation
        super().full_clean()

    def clean_zendesk_ticket(self):
        ticket = self.cleaned_data.get('zendesk_ticket', '')
        if ticket and ticket.strip():  # Only validate if not empty
            if not ticket.isdigit():
                raise forms.ValidationError("Zendesk ticket must contain only numbers")
        return ticket

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            return cleaned_data
            
        # No relationship restrictions based on appliance type
        # Both EDGE and CORE can have any relationship type
        return cleaned_data
    
    def clean_core(self):
        core = self.cleaned_data.get('core', '')
        # Just return the core - validation happens via choices
        return core


# Filter Forms
class OrganizationFilterForm(NetBoxModelFilterSetForm):
    q = forms.CharField(required=False, label="Search")
    tag = TagFilterField(Organization)

    model = Organization


class ISDAFilterForm(NetBoxModelFilterSetForm):
    q = forms.CharField(required=False, label="Search")
    organization = DynamicModelChoiceField(
        queryset=Organization.objects.all(), 
        required=False
    )
    appliance_type = forms.MultipleChoiceField(
        choices=ISDAS.APPLIANCE_CHOICES,
        required=False,
    )
    tag = TagFilterField(ISDAS)

    model = ISDAS


class SCIONLinkAssignmentFilterForm(NetBoxModelFilterSetForm):
    q = forms.CharField(required=False, label="Search")
    isd_as = DynamicModelChoiceField(
        queryset=ISDAS.objects.all(),
        required=False,
        label='ISD-AS'
    )
    relationship = forms.MultipleChoiceField(
        choices=SCIONLinkAssignment.RELATIONSHIP_CHOICES,
        required=False,
    )
    tag = TagFilterField(SCIONLinkAssignment)

    model = SCIONLinkAssignment
