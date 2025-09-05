# Simple initial migration for netbox_scion plugin

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # Create Organization table
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('short_name', models.CharField(max_length=100, unique=True, help_text="Short name for the organization (unique globally)")),
                ('full_name', models.CharField(max_length=200, help_text="Full name of the organization")),
                ('description', models.TextField(blank=True, help_text="Optional description")),
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
                'ordering': ['short_name'],
            },
        ),
        
        # Create ISDAS table
        migrations.CreateModel(
            name='ISDAS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('isd_as', models.CharField(
                    max_length=32,
                    unique=True,
                    validators=[
                        django.core.validators.RegexValidator(
                            regex=r'^\d+-[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9a-fA-F]+$',
                            message="ISD-AS must be in format '{isd}-{as}' (e.g., '1-ff00:0:110')",
                            code='invalid_isd_as'
                        )
                    ],
                    help_text="ISD-AS identifier in format '{isd}-{as}' (e.g., '1-ff00:0:110')"
                )),
                ('description', models.TextField(blank=True, help_text="Optional description")),
                ('cores', models.JSONField(default=list, blank=True, help_text="List of core nodes for this ISD-AS")),
                ('organization', models.ForeignKey(
                    on_delete=models.PROTECT,
                    related_name='isd_ases',
                    to='netbox_scion.organization',
                    help_text="Organization that operates this ISD-AS"
                )),
            ],
            options={
                'verbose_name': 'ISD-AS',
                'verbose_name_plural': 'ISD-ASes',
                'ordering': ['isd_as'],
            },
        ),
        
        # Create SCIONLinkAssignment table
        migrations.CreateModel(
            name='SCIONLinkAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('interface_id', models.PositiveIntegerField(help_text="Interface ID (unique per ISD-AS)")),
                ('customer_id', models.CharField(max_length=100, help_text="Customer identifier")),
                ('customer_name', models.CharField(max_length=100, help_text="Customer name")),
                ('zendesk_ticket', models.CharField(
                    max_length=16,
                    validators=[
                        django.core.validators.RegexValidator(
                            regex=r'^\d+$',
                            message="Zendesk ticket must be a number",
                            code='invalid_ticket'
                        )
                    ],
                    help_text="Zendesk ticket number (numbers only)"
                )),
                ('isd_as', models.ForeignKey(
                    on_delete=models.CASCADE,
                    related_name='link_assignments',
                    to='netbox_scion.isdas',
                    help_text="ISD-AS that owns this interface"
                )),
            ],
            options={
                'verbose_name': 'SCION Link Assignment',
                'verbose_name_plural': 'SCION Link Assignments',
                'ordering': ['isd_as', 'interface_id'],
            },
        ),
        
        # Add the unique constraint
        migrations.AddConstraint(
            model_name='scionlinkassignment',
            constraint=models.UniqueConstraint(fields=['isd_as', 'interface_id'], name='unique_interface_per_isdas'),
        ),
    ]
