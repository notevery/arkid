# Generated by hanbin 3.8 on 2021-06-24 03:30

from django.db import migrations

class Migration(migrations.Migration):

    def add_default_data(apps, schema_editor):
        from tenant.models import Tenant, TenantContactsUserFieldConfig
        tenants = Tenant.active_objects.all()
        for tenant in tenants:
            # 字段可见性
            TenantContactsUserFieldConfig.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                name="用户名",
                data={
                    "visible_type": "所有人可见",
                    "visible_scope": [],
                    "assign_group": [],
                    "assign_user": []
                }
            )
            TenantContactsUserFieldConfig.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                name="姓名",
                data={
                    "visible_type": "所有人可见",
                    "visible_scope": [],
                    "assign_group": [],
                    "assign_user": []
                }
            )
            TenantContactsUserFieldConfig.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                name="电话",
                data={
                    "visible_type": "所有人可见",
                    "visible_scope": [],
                    "assign_group": [],
                    "assign_user": []
                }
            )
            TenantContactsUserFieldConfig.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                name="邮箱",
                data={
                    "visible_type": "所有人可见",
                    "visible_scope": [],
                    "assign_group": [],
                    "assign_user": []
                }
            )
            TenantContactsUserFieldConfig.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                name="职位",
                data={
                    "visible_type": "所有人可见",
                    "visible_scope": [],
                    "assign_group": [],
                    "assign_user": []
                }
            )
       

    dependencies = [
        ('tenant', '0014_auto_20210803_0728'),
    ]

    operations = [
        migrations.RunPython(add_default_data),
    ]