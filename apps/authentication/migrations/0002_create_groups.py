"""
Migration to create the default groups
"""
from django.conf import settings
from django.db import migrations

def create_default_groups(apps, schema_editor):
    """
    Creates the default groups for the application
    """
    group = apps.get_model('auth.Group')
    Permission = apps.get_model('auth.Permission')
    content_type = apps.get_model('contenttypes.ContentType')
    UserModel = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])

    user_content_type = content_type.objects.get_for_model(UserModel)

    add_user_permission, created = Permission.objects.get_or_create(
        codename='add_user', content_type=user_content_type)
    change_user_permission, created = Permission.objects.get_or_create(
        codename='change_user', content_type=user_content_type)
    delete_user_permission, created = Permission.objects.get_or_create(
        codename='delete_user', content_type=user_content_type)
    view_user_permission, created = Permission.objects.get_or_create(
        codename='view_user', content_type=user_content_type)


    admins_group, _ = group.objects.get_or_create(
        name='admins')
    town_hall_employee_group, _ = group.objects.get_or_create(
        name='town_hall_employee_group')
    admin_town_hall_employee_group, _ = group.objects.get_or_create(
        name='admin_town_hall_employee_group')

    # Add permissions to the groups
    admins_group.permissions.add(add_user_permission, change_user_permission,
    delete_user_permission, view_user_permission)
    admin_town_hall_employee_group.permissions.add(add_user_permission,
    change_user_permission, delete_user_permission, view_user_permission)
    town_hall_employee_group.permissions.add(view_user_permission)

class Migration(migrations.Migration):
    """
    Migration to create the default groups
    """


    dependencies = [
        ('authentication', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_default_groups),
    ]
