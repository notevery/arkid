# Generated by Django 3.2.13 on 2022-08-25 04:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('com_longgui_external_idp_gitee', '0002_auto_20220824_0849'),
    ]

    operations = [
        migrations.RenameField(
            model_name='giteeuser',
            old_name='avatar',
            new_name='gitee_avatar',
        ),
        migrations.RenameField(
            model_name='giteeuser',
            old_name='nickname',
            new_name='gitee_nickname',
        ),
    ]
