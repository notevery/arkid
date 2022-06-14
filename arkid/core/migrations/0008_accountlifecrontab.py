# Generated by Django 3.2.13 on 2022-06-01 07:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_merge_0006_languagedata_0006_merge_20220526_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountLifeCrontab',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('name', models.CharField(blank=True, default='', max_length=128, null=True, verbose_name='name')),
                ('config', models.JSONField(blank=True, default=dict, null=True, verbose_name='Config')),
                ('tenant', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.tenant', verbose_name='Tenant')),
            ],
            options={
                'verbose_name': 'Account Life Crontab',
                'verbose_name_plural': 'Account Life Crontab',
            },
        ),
    ]