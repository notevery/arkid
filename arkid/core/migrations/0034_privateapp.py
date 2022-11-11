# Generated by Django 4.0.6 on 2022-11-10 03:29

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_alter_appgroup_apps_alter_tenant_users_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateApp',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('url', models.CharField(blank=True, max_length=1024, null=True, verbose_name='url')),
                ('logo', models.CharField(blank=True, default='', max_length=1024, null=True, verbose_name='logo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('arkstore_category_id', models.IntegerField(default=None, null=True, verbose_name='ArkStore分类ID')),
                ('arkstore_app_id', models.CharField(blank=True, default=None, max_length=1024, null=True, verbose_name='Arkstore app id')),
                ('status', models.CharField(choices=[('install_success', 'Install Success'), ('installing', 'Installing'), ('install_fail', 'Install Fail')], default='installing', max_length=100, verbose_name='Status')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.tenant')),
            ],
            options={
                'verbose_name': 'Private APP',
                'verbose_name_plural': 'Private APP',
            },
        ),
    ]
