# Generated by Django 3.2.13 on 2022-08-24 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('com_longgui_external_idp_wechatscan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wechatscanuser',
            name='avatar',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='头像'),
        ),
        migrations.AddField(
            model_name='wechatscanuser',
            name='nickname',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='昵称'),
        ),
    ]
