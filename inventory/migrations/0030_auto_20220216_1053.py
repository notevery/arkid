# Generated by Django 3.2.10 on 2022-02-16 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0029_merge_20210922_0729'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='action',
            field=models.CharField(default='', max_length=256, null=True, verbose_name='请求方法'),
        ),
        migrations.AddField(
            model_name='permission',
            name='description',
            field=models.CharField(default='', max_length=512, null=True, verbose_name='描述'),
        ),
        migrations.AddField(
            model_name='permission',
            name='group_info',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='inventory.group', verbose_name='分组'),
        ),
        migrations.AddField(
            model_name='permission',
            name='operation_id',
            field=models.CharField(default='', max_length=256, null=True, verbose_name='操作id'),
        ),
        migrations.AddField(
            model_name='permission',
            name='request_url',
            field=models.CharField(default='', max_length=256, null=True, verbose_name='请求地址'),
        ),
    ]