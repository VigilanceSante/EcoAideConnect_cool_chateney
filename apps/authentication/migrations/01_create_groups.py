from django.db import migrations

# Il faut je pense retirer le startup user admin il sert a rien
# Peut être que le admin user et standard user built in de django peut etre suffisant
# Réfléchir aux potentiels rôles des employés de mairie

def create_default_groups(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    permission = apps.get_model('auth', 'Permission')
    content_type = apps.get_model('contenttypes.ContentType')

    user_content_type = content_type.objects.get(app_label='auth', model='user')

    add_user_permission = permission.objects.get(codename='add_user',
    content_type=user_content_type)
    change_user_permission = permission.objects.get(codename='change_user',
    content_type=user_content_type)
    delete_user_permission = permission.objects.get(codename='delete_user',
    content_type=user_content_type)
    view_user_permission = permission.objects.get(codename='view_user',
    content_type=user_content_type)


    admins_group = group.objects.get_or_create(name='admins')

    town_hall_employee_group = group.objects.get_or_create(
        name='town_hall_employee_group')

    admin_town_hall_employee_group = group.objects.get_or_create(
        name='admin_town_hall_employee_group')

    admin_startup_group = group.objects.get_or_create(
        name='admin_startup_group')


    admins_group.permissions.add(add_user_permission,
    change_user_permission, delete_user_permission, view_user_permission)

    admin_town_hall_employee_group.permissions.add(add_user_permission,
    change_user_permission, delete_user_permission, view_user_permission)

    admin_startup_group.permissions.add(add_user_permission,
    change_user_permission, delete_user_permission, view_user_permission)

    town_hall_employee_group.permissions.add(view_user_permission)


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(create_default_groups),
    ]
