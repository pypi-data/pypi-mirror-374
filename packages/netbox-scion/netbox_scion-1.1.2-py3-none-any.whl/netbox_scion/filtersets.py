import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .models import Organization, ISDAS, SCIONLinkAssignment


class OrganizationFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    class Meta:
        model = Organization
        fields = ['id', 'short_name', 'full_name']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(short_name__icontains=value)
                | Q(full_name__icontains=value)
                | Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class ISDAFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    appliance_type = django_filters.ChoiceFilter(
        choices=ISDAS.APPLIANCE_CHOICES,
        label='Appliance Type'
    )
    
    class Meta:
        model = ISDAS
        fields = ['id', 'isd_as', 'appliance_type', 'organization']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(isd_as__icontains=value)
                | Q(description__icontains=value)
                | Q(organization__short_name__icontains=value)
                | Q(organization__full_name__icontains=value)
        )
        return queryset.filter(qs_filter)


class SCIONLinkAssignmentFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    class Meta:
        model = SCIONLinkAssignment
        fields = ['id', 'isd_as', 'core', 'relationship', 'customer_name', 'customer_id']

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
                Q(isd_as__isd_as__icontains=value)
                | Q(core__icontains=value)
                | Q(customer_name__icontains=value)
                | Q(customer_id__icontains=value)
                | Q(zendesk_ticket__icontains=value)
        )
        return queryset.filter(qs_filter)