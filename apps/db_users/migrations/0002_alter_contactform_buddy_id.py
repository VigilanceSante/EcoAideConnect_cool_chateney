# Generated by Django 5.1.1 on 2024-10-09 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db_users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactform',
            name='buddy_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
