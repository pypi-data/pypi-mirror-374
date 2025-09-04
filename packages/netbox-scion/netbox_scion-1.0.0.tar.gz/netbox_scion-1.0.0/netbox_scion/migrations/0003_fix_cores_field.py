# Generated migration to fix cores field type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_scion', '0002_add_custom_field_data'),
    ]

    operations = [
        # Change cores field from ArrayField to JSONField for consistency
        migrations.AlterField(
            model_name='isdas',
            name='cores',
            field=models.JSONField(blank=True, default=list, help_text='List of core nodes for this ISD-AS'),
        ),
    ]
