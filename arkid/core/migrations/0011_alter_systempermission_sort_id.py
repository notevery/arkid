# Generated by Django 3.2.13 on 2022-05-10 11:20

import arkid.core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_systempermission_sort_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systempermission',
            name='sort_id',
            field=models.IntegerField(default=arkid.core.models.SystemPermission.anto_sort, verbose_name='Sort ID'),
        ),
    ]
