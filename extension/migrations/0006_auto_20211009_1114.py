# Generated by Django 3.2.6 on 2021-10-09 11:14

from django.db import migrations


def add_default_enabled_extensions(apps, schema_editor):
    Extension = apps.get_model('extension', 'Extension')

    Extension.objects.get_or_create(
        type='mysql_statistics',
        data={},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('extension', '0005_auto_20210824_0920'),
    ]

    operations = [
        migrations.RunPython(add_default_enabled_extensions),
    ]