# Generated by Django 3.2.13 on 2022-08-10 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('com_longgui_auth_factor_email', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremail',
            name='email',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Email'),
        ),
    ]
