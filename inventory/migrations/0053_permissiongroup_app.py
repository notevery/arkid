# Generated by Django 3.2.10 on 2022-03-28 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_app_logo'),
        ('inventory', '0052_auto_20220328_0938'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissiongroup',
            name='app',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.app'),
        ),
    ]
