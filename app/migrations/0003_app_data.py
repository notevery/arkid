# Generated by Django 3.1.7 on 2021-03-25 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_app_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='data',
            field=models.JSONField(blank=True, default={}),
            preserve_default=False,
        ),
    ]