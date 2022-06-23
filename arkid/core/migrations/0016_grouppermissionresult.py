# Generated by Django 3.2.13 on 2022-06-23 08:19

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_alter_app_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPermissionResult',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('result', models.CharField(blank=True, max_length=1024, null=True, verbose_name='权限结果')),
                ('app', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.app', verbose_name='App')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.tenant', verbose_name='租户')),
                ('user_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.usergroup', verbose_name='用户')),
            ],
            options={
                'verbose_name': 'GroupPermissionResult',
                'verbose_name_plural': 'GroupPermissionResult',
            },
        ),
    ]
