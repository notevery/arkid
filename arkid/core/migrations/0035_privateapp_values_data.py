# Generated by Django 4.0.6 on 2022-11-10 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_privateapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='privateapp',
            name='values_data',
            field=models.TextField(blank=True, null=True, verbose_name='Values Data'),
        ),
    ]
