# Generated by Django 3.2.10 on 2022-02-18 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0032_auto_20220217_0752'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='is_update',
            field=models.IntegerField(default=0, verbose_name='是否更新'),
        ),
    ]
