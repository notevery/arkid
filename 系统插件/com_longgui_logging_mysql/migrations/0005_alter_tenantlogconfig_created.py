# Generated by Django 4.0.6 on 2022-09-06 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('com_longgui_logging_mysql', '0004_log_is_tenant_admin_alter_log_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenantlogconfig',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='创建时间'),
        ),
    ]
