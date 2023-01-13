# Generated by Django 4.0.6 on 2022-11-21 07:29

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0035_privateapp_values_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserQRCode',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('qrcode_id', models.CharField(max_length=256, verbose_name='QRCode ID')),
                ('session_key', models.CharField(default='', max_length=256, verbose_name='Client Session key')),
                ('status', models.CharField(choices=[('created', 'QRCode Created'), ('expired', 'QRCode Expired'), ('scanned', 'QRCode Scanned'), ('confirmed', 'QRCode Confirmed'), ('canceled', 'QRCode Canceled')], default='created', max_length=50, verbose_name='Status')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='qrcode_set', related_query_name='qrcodes', to='core.user', verbose_name='User')),
            ],
        ),
    ]
