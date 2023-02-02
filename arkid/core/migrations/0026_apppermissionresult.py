# Generated by Django 3.2.13 on 2022-08-31 03:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_merge_20220830_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppPermissionResult',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('result', models.CharField(blank=True, max_length=1024, null=True, verbose_name='权限结果')),
                ('app', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='select_app', to='core.app', verbose_name='App')),
                ('self_app', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='self_app', to='core.app', verbose_name='自身应用')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.tenant', verbose_name='租户')),
            ],
            options={
                'verbose_name': 'AppPermissionResult',
                'verbose_name_plural': 'AppPermissionResult',
            },
        ),
    ]