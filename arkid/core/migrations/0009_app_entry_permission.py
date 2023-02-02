# Generated by Django 3.2.13 on 2022-05-31 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_tenant_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='entry_permission',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.systempermission'),
        ),
    ]