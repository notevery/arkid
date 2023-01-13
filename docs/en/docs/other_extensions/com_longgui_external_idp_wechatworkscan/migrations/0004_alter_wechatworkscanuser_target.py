# Generated by Django 4.0.6 on 2022-11-10 03:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_expiringtoken_active_date'),
        ('com_longgui_external_idp_wechatworkscan', '0003_auto_20220825_0403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wechatworkscanuser',
            name='target',
            field=models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s', to='core.user'),
        ),
    ]
