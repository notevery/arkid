# Generated by Django 3.2.13 on 2022-09-05 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('com_longgui_auth_factor_mobile', '0002_alter_usermobile_target'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermobile',
            name='mobile',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Mobile'),
        ),
    ]
