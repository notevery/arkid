# Generated by Django 3.2.6 on 2021-11-15 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_app_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='logo',
            field=models.CharField(blank=True, default='', max_length=1024, null=True),
        ),
    ]