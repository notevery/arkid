# Generated by Django 3.2.13 on 2022-08-25 04:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('com_longgui_external_idp_feishu', '0002_auto_20220824_0855'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feishuuser',
            old_name='avatar',
            new_name='feishu_avatar',
        ),
        migrations.RenameField(
            model_name='feishuuser',
            old_name='nickname',
            new_name='feishu_nickname',
        ),
    ]
