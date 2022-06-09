# Generated by Django 3.2.10 on 2022-02-17 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0032_add_default_tenant_config'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('inventory', '0031_auto_20220217_0724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='content_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upermission_content_type', to='contenttypes.contenttype', verbose_name='content type'),
        ),
        migrations.AlterField(
            model_name='permission',
            name='tenant',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='tenant.tenant'),
        ),
    ]