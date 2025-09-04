# Generated migration for adding custom_field_data columns

from django.db import migrations, models


def add_custom_field_data_if_not_exists(apps, schema_editor):
    """
    Add custom_field_data columns only if they don't already exist.
    Also update any existing NULL values to empty dict.
    """
    db_alias = schema_editor.connection.alias
    
    # Check and add columns if they don't exist
    with schema_editor.connection.cursor() as cursor:
        # Check Organization table
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='netbox_scion_organization' AND column_name='custom_field_data'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE netbox_scion_organization 
                ADD COLUMN custom_field_data jsonb DEFAULT '{}' NOT NULL
            """)
        else:
            # Column exists, update NULL values and set default
            cursor.execute("""
                UPDATE netbox_scion_organization 
                SET custom_field_data = '{}' 
                WHERE custom_field_data IS NULL
            """)
            cursor.execute("""
                ALTER TABLE netbox_scion_organization 
                ALTER COLUMN custom_field_data SET DEFAULT '{}'
            """)
            cursor.execute("""
                ALTER TABLE netbox_scion_organization 
                ALTER COLUMN custom_field_data SET NOT NULL
            """)

        # Check ISDAS table
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='netbox_scion_isdas' AND column_name='custom_field_data'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE netbox_scion_isdas 
                ADD COLUMN custom_field_data jsonb DEFAULT '{}' NOT NULL
            """)
        else:
            cursor.execute("""
                UPDATE netbox_scion_isdas 
                SET custom_field_data = '{}' 
                WHERE custom_field_data IS NULL
            """)
            cursor.execute("""
                ALTER TABLE netbox_scion_isdas 
                ALTER COLUMN custom_field_data SET DEFAULT '{}'
            """)
            cursor.execute("""
                ALTER TABLE netbox_scion_isdas 
                ALTER COLUMN custom_field_data SET NOT NULL
            """)

        # Check SCIONLinkAssignment table
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='netbox_scion_scionlinkassignment' AND column_name='custom_field_data'
        """)
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE netbox_scion_scionlinkassignment 
                ADD COLUMN custom_field_data jsonb DEFAULT '{}' NOT NULL
            """)
        else:
            cursor.execute("""
                UPDATE netbox_scion_scionlinkassignment 
                SET custom_field_data = '{}' 
                WHERE custom_field_data IS NULL
            """)
            cursor.execute("""
                ALTER TABLE netbox_scion_scionlinkassignment 
                ALTER COLUMN custom_field_data SET DEFAULT '{}'
            """)
            cursor.execute("""
                ALTER TABLE netbox_scion_scionlinkassignment 
                ALTER COLUMN custom_field_data SET NOT NULL
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_scion', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_custom_field_data_if_not_exists),
    ]
