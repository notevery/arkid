from ninja import Schema, ModelSchema
from arkid.core import extension
from arkid.core.api import api
from typing import Union
from typing_extensions import Annotated
from pydantic import Field
from arkid.core.extension import Extension
from arkid.extension.models import TenantExtensionConfig, TenantExtension
from arkid.core.schema import RootSchema
from arkid.core.translation import gettext_default as _

ExtensionConfigSchemaIn = Extension.create_config_schema(
    'ExtensionConfigSchemaIn',
)


class ExtensionConfigCreateSchemaOut(Schema):
    config_id: str


@api.post("/{tenant_id}/extension/{extension_id}/config/", response=ExtensionConfigCreateSchemaOut,  tags=['租户插件'], auth=None)
def create_extension_config(request, tenant_id: str, extension_id: str, data: ExtensionConfigSchemaIn):
    '''租户下，创建插件运行时配置'''
    config = TenantExtensionConfig.objects.create(
        tenant_id=tenant_id,
        extension_id=extension_id,
        config=data.config.dict(),
    )
    return {"config_id": config.id.hex}


ExtensionSettingsCreateIn = Extension.create_settings_schema(
    'ExtensionSettingsCreateIn')


class ExtensionSettingsCreateOut(Schema):
    settings_id: str


@api.post("/{tenant_id}/extension/{extension_id}/settings/", response=ExtensionSettingsCreateOut,  tags=['租户插件'], auth=None)
def create_extension_settings(request, tenant_id: str, extension_id: str, data: ExtensionSettingsCreateIn):
    '''租户下，创建插件配置'''
    settings = TenantExtension.objects.create(
        tenant_id=tenant_id,
        extension_id=extension_id,
        settings=data.settings.dict(),
    )
    return {"settings_id": settings.id.hex}


# @api.get("/extensions/{extension_id}", response=ExtensionDetailOut)
# def get_extension(request, extension_id: str):
#     extension = get_object_or_404(Extension, uuid=extension_id, user=request.user)
#     return extension


# @api.get("/extensions", response=List[ExtensionOut])
# def list_extensions(request, status: str = None):
#     if not status:
#         qs = Extension.active_objects.filter(user=request.user)
#     else:
#         qs = Extension.active_objects.filter(user=request.user, status=status)
#     return qs


# @operation(roles=["tenant-user", "platform-user"])
# def update_extension(request, extension_id: str, payload: ExtensionIn):
#     extension = get_object_or_404(Extension, uuid=extension_id, user=request.user)
#     data = payload.dict()
#     file_name = data.pop("file_name")
#     categories = data.pop("categories")
#     price = data.pop("price")
#     price_type = data.pop("price_type")
#     cost_discount = data.pop("cost_discount")

#     labels = data.pop("labels")
#     data["file"] = File.active_objects.filter(name=file_name).first()
#     data["user"] = request.user
#     data["tenant"] = request.user.tenant
#     for attr, value in data.items():
#         setattr(extension, attr, value)
#     if categories:
#         for category in categories:
#             category = Category.active_objects.filter(name=category).first()
#             if category:
#                 extension.categories.add(category)
#     if price:
#         extension.prices.clear()
#         price, is_create = Price.objects.get_or_create(
#             type=price_type,
#             standard_price=price,
#             cost_discount=cost_discount,
#         )
#         extension.prices.add(price)
#     if labels:
#         extension.label = " ".join(labels)
#     extension.save()
#     return {"success": True}


# @api.delete("/extensions/{extension_id}")
# def delete_extension(request, extension_id: str):
#     extension = get_object_or_404(Extension, uuid=extension_id)
#     extension.delete()
#     return {"success": True}

@api.get("/tenant/{tenant_id}/extensions/", tags=["租户插件"],auth=None)
def get_extensions(request, tenant_id: str):
    """ 租户插件列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/extensions/{id}/", tags=["租户插件"],auth=None)
def get_extension(request, tenant_id: str, id: str):
    """ 获取租户插件,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/extensions/{id}/", tags=["租户插件"],auth=None)
def delete_extension(request, tenant_id: str, id: str):
    """ 删除租户插件,TODO
    """
    return {}