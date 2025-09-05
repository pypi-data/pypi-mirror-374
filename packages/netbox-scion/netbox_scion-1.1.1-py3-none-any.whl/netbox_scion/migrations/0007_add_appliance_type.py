from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_scion', '0006_make_zendesk_ticket_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='isdas',
            name='appliance_type',
            field=models.CharField(
                choices=[('CORE', 'CORE'), ('EDGE', 'EDGE'), ('GATE', 'GATE')],
                default='CORE',
                help_text='Type of appliance for this ISD-AS',
                max_length=20,
                verbose_name='Appliance Type'
            ),
            preserve_default=True,
        ),
    ]
