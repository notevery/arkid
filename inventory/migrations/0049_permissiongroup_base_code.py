# Generated by Django 3.2.10 on 2022-03-21 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0048_permission_base_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissiongroup',
            name='base_code',
            field=models.CharField(blank=True, default='', max_length=256, null=True, verbose_name='应用code'),
        ),
    ]
