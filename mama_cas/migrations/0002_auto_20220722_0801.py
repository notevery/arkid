# Generated by Django 3.2.13 on 2022-07-22 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mama_cas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proxygrantingticket',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='proxyticket',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='serviceticket',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
