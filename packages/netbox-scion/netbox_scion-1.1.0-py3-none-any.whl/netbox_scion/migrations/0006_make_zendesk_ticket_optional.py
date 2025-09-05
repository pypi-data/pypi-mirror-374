# Generated migration for making zendesk_ticket optional

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_scion', '0005_add_relationship_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scionlinkassignment',
            name='zendesk_ticket',
            field=models.CharField(blank=True, help_text='Zendesk ticket number (numbers only, optional)', max_length=16, validators=[django.core.validators.RegexValidator(code='invalid_ticket', message='Zendesk ticket must be a number', regex='^\\d+$')]),
        ),
    ]
