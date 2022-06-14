from uuid import UUID
from typing import List
from ninja import Field
from ninja import Schema
from ninja import ModelSchema
from django.db import transaction
from ninja.pagination import paginate
from arkid.core.error import ErrorCode
from arkid.core.api import api, operation
from django.shortcuts import get_object_or_404
from arkid.core.models import Permission, SystemPermission
from arkid.core.event import Event, dispatch_event
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from arkid.core.event import (
    CREATE_GROUP_PERMISSION, UPDATE_GROUP_PERMISSION, DELETE_GROUP_PERMISSION,
    REMOVE_GROUP_PERMISSION_PERMISSION, UPDATE_GROUP_PERMISSION_PERMISSION,
)
from arkid.core.translation import gettext_default as _

import uuid

class PermissionGroupListSchemaOut(ModelSchema):

    app_id: UUID = Field(default=None)

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'is_system']


class PermissionGroupDetailSchemaOut(ModelSchema):

    parent_id: UUID = Field(default=None)

    class Config:
        model = Permission
        model_fields = ['id', 'name', 'category']


class PermissionGroupSchemaOut(Schema):
    permission_group_id: str


class PermissionGroupSchemaIn(ModelSchema):

    app_id: str
    parent_id: str = None

    class Config:
        model = Permission
        model_fields = ['name']


class PermissionGroupEditSchemaIn(ModelSchema):

    parent_id: str = None

    class Config:
        model = Permission
        model_fields = ['name']

class PermissionListSchemaOut(ModelSchema):

    class Config:
        model = SystemPermission
        model_fields = ['id', 'name', 'category', 'is_system']


class PermissionListSelectSchemaOut(Schema):

    id: UUID = Field(default=None)
    in_current: bool
    name: str
    category: str
    is_system: bool


class PermissionSchemaIn(Schema):
    permission_id: str

@api.get("/tenant/{tenant_id}/permission_groups/", tags=["权限分组"], response=List[PermissionGroupListSchemaOut], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate
def get_permission_groups(request, tenant_id: str,  parent_id: str = None,  app_id: str = None):
    """ 权限分组列表
    """
    # 只允许非系统并且有应用的分组编辑
    tenant = request.tenant
    systempermissions = SystemPermission.valid_objects.filter(
        category='group'
    )
    permissions = Permission.valid_objects.filter(
        tenant=tenant,
        category='group'
    )
    if parent_id:
        systempermissions = systempermissions.filter(parent_id=parent_id)
        permissions = permissions.filter(parent_id=parent_id)
    else:
        systempermissions = systempermissions.filter(parent_id__isnull=True)
        permissions = permissions.filter(parent_id__isnull=True)
    if app_id:
        systempermissions = systempermissions.filter(app_id=app_id)
        permissions = permissions.filter(app_id=app_id)
    return list(systempermissions)+list(permissions)

@api.get("/tenant/{tenant_id}/permission_groups/{id}/", response=PermissionGroupDetailSchemaOut, tags=["权限分组"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_permission_group(request, tenant_id: str, id: str):
    """ 获取权限分组
    """
    tenant = request.tenant
    if tenant.is_platform_tenant:
        return get_object_or_404(SystemPermission, id=id, is_del=False, category='group')
    else:
        return get_object_or_404(Permission, id=id, is_del=False, category='group')

@transaction.atomic
@api.post("/tenant/{tenant_id}/permission_groups/", response=PermissionGroupSchemaOut, tags=["权限分组"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_permission_group(request, tenant_id: str, data: PermissionGroupSchemaIn):
    """ 创建权限分组
    """
    permission = Permission()
    permission.tenant_id = tenant_id
    permission.name = data.name
    permission.category = 'group'
    permission.code = 'other_{}'.format(uuid.uuid4())
    if data.parent_id:
        permission.parent_id = data.parent_id
    permission.app_id = data.app_id
    permission.is_system = False
    permission.save()
    # 分发事件开始
    result = dispatch_event(Event(tag=CREATE_GROUP_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {"permission_group_id": permission.id.hex}

@api.put("/tenant/{tenant_id}/permission_groups/{id}/", tags=["权限分组"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_permission_group(request, tenant_id: str, id: str, data: PermissionGroupEditSchemaIn):
    """ 编辑权限分组
    """
    # tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission = get_object_or_404(SystemPermission, id=id, is_del=False, category='group')
    # else:
    #     permission = get_object_or_404(Permission, id=id, is_del=False, category='group')
    # permission = SystemPermission.valid_objects.filter(id=id, category='group').first()
    # if permission is None:
    permission = Permission.valid_objects.filter(id=id, category='group').first()
    permission.name = data.name
    if data.parent_id:
        permission.parent_id = data.parent_id
    # if data.app_id:
    #     permission.app_id = data.app_id
    permission.save()
    # 分发事件开始
    dispatch_event(Event(tag=UPDATE_GROUP_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {'error': ErrorCode.OK.value}

@api.delete("/tenant/{tenant_id}/permission_groups/{id}/", tags=["权限分组"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_permission_group(request, tenant_id: str, id: str):
    """ 删除权限分组
    """
    # tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission = get_object_or_404(SystemPermission, id=id, is_del=False, category='group')
    # else:
    #     permission = get_object_or_404(Permission, id=id, is_del=False, category='group')
    permission = SystemPermission.valid_objects.filter(id=id, category='group').first()
    if permission is None:
        permission = Permission.valid_objects.filter(id=id, category='group').first()
    permission.delete()
    # 分发事件开始
    dispatch_event(Event(tag=DELETE_GROUP_PERMISSION, tenant=request.tenant, request=request, data=permission))
    # 分发事件结束
    return {'error': ErrorCode.OK.value}

@api.get("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/", response=List[PermissionListSchemaOut], tags=["权限分组"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate
def get_permissions_from_group(request, tenant_id: str, permission_group_id: str):
    """ 获取当前分组的权限列表
    """
    permission = SystemPermission.valid_objects.filter(id=permission_group_id).first()
    if permission is None:
        permission = Permission.valid_objects.filter(id=permission_group_id).first()
    return permission.container.all()
    # tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission = get_object_or_404(SystemPermission, id=permission_group_id, is_del=False)
    # else:
    #     permission = get_object_or_404(Permission, id=permission_group_id, is_del=False)
    

@api.delete("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/{id}/", tags=["权限分组"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def remove_permission_from_group(request, tenant_id: str, permission_group_id: str, id:str):
    """ 将权限移除出权限分组
    """
    # 只允许非arkid的操作
    # tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission_group = get_object_or_404(SystemPermission, id=permission_group_id, is_del=False, category='group')
    #     permission = get_object_or_404(SystemPermission, id=id, is_del=False)
    # else:
    permission_group = get_object_or_404(Permission, id=permission_group_id, is_del=False, category='group')
    permission = get_object_or_404(Permission, id=id, is_del=False)
    if permission_group and permission:
        permission_group.container.remove(permission)
        # 分发事件开始
        dispatch_event(Event(tag=REMOVE_GROUP_PERMISSION_PERMISSION, tenant=request.tenant, request=request, data=permission_group))
        # 分发事件结束
    return {'error': ErrorCode.OK.value}

@api.post("/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/", tags=["权限分组"],auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_permissions_from_group(request, tenant_id: str, permission_group_id: str, data: PermissionSchemaIn):
    """ 更新当前分组的权限列表
    """
    # 只允许非arkid的操作
    tenant = request.tenant
    # if tenant.is_platform_tenant:
    #     permission_group = get_object_or_404(SystemPermission, id=permission_group_id, is_del=False, category='group')
    #     permission = get_object_or_404(SystemPermission, id=data.permission_id, is_del=False)
    # else:
    permission_group = get_object_or_404(Permission, id=permission_group_id, is_del=False, category='group')
    permission = get_object_or_404(Permission, id=data.permission_id, is_del=False)
    if permission_group and permission:
        permission_group.container.add(permission)
        # 分发事件开始
        dispatch_event(Event(tag=UPDATE_GROUP_PERMISSION_PERMISSION, tenant=tenant, request=request, data=permission_group))
        # 分发事件结束
    return {'error': ErrorCode.OK.value}

@api.get("/tenant/{tenant_id}/permission_groups/{permission_group_id}/select_permissions/", response=List[PermissionListSelectSchemaOut], tags=["权限分组"], auth=None)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate
def get_select_permissions(request, tenant_id: str, permission_group_id: str):
    """ 获取所有权限并附加是否在当前分组的状态
    """
    # 只允许非arkid的操作
    permission_group = SystemPermission.valid_objects.filter(id=id, category='group').first()
    if permission_group is None:
        permission_group = Permission.valid_objects.filter(id=id, category='group').first()
    if isinstance(permission_group, SystemPermission):
        # permission_group = get_object_or_404(SystemPermission, id=permission_group_id, is_del=False, category='group')
        containers = permission_group.container.all()
        ids = []
        for container in containers:
            ids.append(container.id.hex)

        permissions = SystemPermission.valid_objects.exclude(category='group')
        for permission in permissions:
            id_hex = permission.id.hex
            if id_hex in ids:
                permission.in_current = True
            else:
                permission.in_current = False
    else:
        containers = permission_group.container.all()
        ids = []
        for container in containers:
            ids.append(container.id.hex)
        permissions = Permission.valid_objects.filter(tenant=permission_group.tenant).exclude(category='group')
        for permission in permissions:
            id_hex = permission.id.hex
            if id_hex in ids:
                permission.in_current = True
            else:
                permission.in_current = False
    return permissions

