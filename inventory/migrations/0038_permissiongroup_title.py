# Generated by Django 3.2.10 on 2022-02-22 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0037_permissiongroup_en_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissiongroup',
            name='title',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='顶级标题'),
        ),
    ]
