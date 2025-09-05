from netbox.search import SearchIndex, register_search
from .models import Organization, ISDAS, SCIONLinkAssignment


@register_search
class OrganizationIndex(SearchIndex):
    model = Organization
    fields = (
        ('short_name', 100),
        ('full_name', 200),
        ('description', 500),
    )


@register_search
class ISDAIndex(SearchIndex):
    model = ISDAS
    fields = (
        ('isd_as', 100),
        ('description', 500),
    )


@register_search
class SCIONLinkAssignmentIndex(SearchIndex):
    model = SCIONLinkAssignment
    fields = (
        ('customer_id', 100),
        ('customer_name', 200),
        ('relationship', 250),
        ('zendesk_ticket', 300),
    )
