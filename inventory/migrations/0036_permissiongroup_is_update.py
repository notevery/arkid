# Generated by Django 3.2.10 on 2022-02-22 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0035_rename_permission_parent_permissiongroup_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissiongroup',
            name='is_update',
            field=models.BooleanField(default=False, verbose_name='是否更新'),
        ),
    ]
