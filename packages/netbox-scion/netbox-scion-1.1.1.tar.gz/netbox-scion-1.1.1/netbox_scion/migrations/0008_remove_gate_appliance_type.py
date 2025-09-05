from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_scion', '0007_add_appliance_type'),
    ]

    operations = [
        # First update any existing GATE appliances to EDGE
        migrations.RunSQL(
            "UPDATE netbox_scion_isdas SET appliance_type = 'EDGE' WHERE appliance_type = 'GATE';",
            reverse_sql="UPDATE netbox_scion_isdas SET appliance_type = 'GATE' WHERE appliance_type = 'EDGE';"
        ),
        # Then update the field choices (this is primarily for documentation)
        migrations.AlterField(
            model_name='isdas',
            name='appliance_type',
            field=models.CharField(
                choices=[('CORE', 'CORE'), ('EDGE', 'EDGE')],
                help_text='Type of appliance for this ISD-AS',
                max_length=20,
                verbose_name='Appliance Type'
            ),
        ),
    ]
