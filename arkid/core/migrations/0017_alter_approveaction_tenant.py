# Generated by Django 3.2.13 on 2022-07-14 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_grouppermissionresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approveaction',
            name='tenant',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approve_action_set', related_query_name='actions', to='core.tenant', verbose_name='Tenant'),
        ),
    ]