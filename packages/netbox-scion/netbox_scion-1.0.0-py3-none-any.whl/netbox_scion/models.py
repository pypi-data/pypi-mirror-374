from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator
from netbox.models import NetBoxModel

try:
    from django.contrib.postgres.fields import ArrayField
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class Organization(NetBoxModel):
    """
    An organization that operates ISD-ASes.
    """
    short_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Short name for the organization (unique globally)"
    )
    full_name = models.CharField(
        max_length=200,
        help_text="Full name of the organization"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description"
    )

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ['short_name']

    def __str__(self):
        return self.short_name

    @property
    def display(self):
        return self.short_name

    def get_absolute_url(self):
        return reverse('plugins:netbox_scion:organization', args=[self.pk])


class ISDAS(NetBoxModel):
    """
    An ISD-AS (Isolation Domain - Autonomous System) in the SCION network.
    """
    # Updated regex to support both formats: 1-ff00:0:110 and 1-1
    ISD_AS_REGEX = r'^\d+-([0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+|\d+)$'
    
    isd_as = models.CharField(
        max_length=32,
        unique=True,
        validators=[
            RegexValidator(
                regex=ISD_AS_REGEX,
                message="ISD-AS must be in format '{isd}-{as}' (e.g., '1-ff00:0:110' or '1-1')",
                code='invalid_isd_as'
            )
        ],
        help_text="ISD-AS identifier in format '{isd}-{as}' (e.g., '1-ff00:0:110' or '1-1')"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='isd_ases',
        help_text="Organization that operates this ISD-AS"
    )
    
    # Use JSONField for consistency with NetBox
    cores = models.JSONField(
        default=list,
        blank=True,
        help_text="List of core nodes for this ISD-AS"
    )

    class Meta:
        verbose_name = "ISD-AS"
        verbose_name_plural = "ISD-ASes"
        ordering = ['isd_as']

    def __str__(self):
        return self.isd_as

    @property
    def display(self):
        return self.isd_as

    def get_absolute_url(self):
        return reverse('plugins:netbox_scion:isdas', args=[self.pk])

    @property
    def cores_display(self):
        """Return cores as a comma-separated string for display"""
        if isinstance(self.cores, list):
            return ', '.join(self.cores)
        return str(self.cores)


class SCIONLinkAssignment(NetBoxModel):
    """
    Assignment of a SCION link interface to a customer.
    """
    
    # Relationship choices
    RELATIONSHIP_PARENT = 'PARENT'
    RELATIONSHIP_CHILD = 'CHILD'
    RELATIONSHIP_CORE = 'CORE'
    
    RELATIONSHIP_CHOICES = [
        (RELATIONSHIP_PARENT, 'PARENT'),
        (RELATIONSHIP_CHILD, 'CHILD'),
        (RELATIONSHIP_CORE, 'CORE'),
    ]
    
    isd_as = models.ForeignKey(
        ISDAS,
        on_delete=models.CASCADE,
        related_name='link_assignments',
        verbose_name="ISD-AS",
        help_text="ISD-AS that owns this interface"
    )
    core = models.CharField(
        max_length=255,
        verbose_name="Core",
        help_text="Core node for this assignment"
    )
    interface_id = models.PositiveIntegerField(
        verbose_name="Interface ID",
        help_text="Interface ID (unique per ISD-AS)"
    )
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        verbose_name="Relationship",
        help_text="Relationship type of this SCION link"
    )
    customer_id = models.CharField(
        max_length=100,
        help_text="Customer identifier"
    )
    customer_name = models.CharField(
        max_length=100,
        help_text="Customer name"
    )
    zendesk_ticket = models.CharField(
        max_length=16,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="Zendesk ticket must be a number",
                code='invalid_ticket'
            )
        ],
        help_text="Zendesk ticket number (numbers only)"
    )

    class Meta:
        verbose_name = "SCION Link Assignment"
        verbose_name_plural = "SCION Link Assignments"
        ordering = ['isd_as', 'interface_id']
        constraints = [
            models.UniqueConstraint(
                fields=['isd_as', 'interface_id'],
                name='unique_interface_per_isdas'
            )
        ]

    def __str__(self):
        return f"{self.isd_as} - Interface {self.interface_id}"

    @property
    def display(self):
        return f"{self.isd_as} - Interface {self.interface_id}"

    def get_absolute_url(self):
        return reverse('plugins:netbox_scion:scionlinkassignment', args=[self.pk])

    def get_zendesk_url(self):
        """Return the full Zendesk URL for this ticket"""
        return f"https://anapaya.zendesk.com/agent/tickets/{self.zendesk_ticket}"
