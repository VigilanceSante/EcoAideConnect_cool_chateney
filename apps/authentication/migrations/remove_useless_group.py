"""
Migration to remove unwanted group from the database
"""
from django.db import migrations

def remove_unwanted_group(apps, schema_editor):
    """
    Removes the unwanted group from the database
    """
    Group = apps.get_model('auth', 'Group')

    
    Group.objects.filter(name='admin_startup_group').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', 'create_groups'),
    ]

    operations = [
        migrations.RunPython(remove_unwanted_group),
    ]
