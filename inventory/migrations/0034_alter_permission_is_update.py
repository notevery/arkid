# Generated by Django 3.2.10 on 2022-02-18 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0033_permission_is_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='is_update',
            field=models.BooleanField(default=False, verbose_name='是否更新'),
        ),
    ]