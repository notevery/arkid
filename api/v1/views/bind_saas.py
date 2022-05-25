from arkid.core.models import Tenant
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from arkid.common.bind_saas import (
    create_oidc_app,
    get_bind_info,
    update_saas_binding,
    create_saas_binding,
    create_arkidstore_login_app,
    create_arkid_saas_login_app,
    bind_saas,
)
from ninja import Schema
from pydantic import Field
from typing import Optional
from arkid.core.api import api


class BindSaasSchemaOut(Schema):
    company_name: str = Field(readonly=True)
    contact_person: str = Field(readonly=True)
    email: Optional[str] = Field(readonly=True, default='')
    mobile: str = Field(readonly=True)
    # local_tenant_id: str = Field(hidden=True)
    # local_tenant_slug: str = Field(hidden=True)
    saas_tenant_id: str = Field(readonly=True)
    saas_tenant_slug: Optional[str]  = Field(readonly=True, default='')
    # saas_tenant_url: str = Field(hidden=True)


class BindSaasSlugSchemaOut(Schema):
    saas_tenant_slug: Optional[str]


class BindSaasInfoSchemaOut(Schema):
    company_name: str
    contact_person: str
    email: Optional[str]
    mobile: str


@api.get("/tenant/{tenant_id}/bind_saas/", tags=['bind_saas'], response=BindSaasSchemaOut)
def get_bind_saas(request, tenant_id: str):
    """
    查询 saas 绑定信息
    """
    bind_info = get_bind_info(tenant_id)
    return bind_info


@api.get("/tenant/{tenant_id}/bind_saas/slug/", tags=['bind_saas'], response=BindSaasSlugSchemaOut)
def get_bind_saas_slug(request, tenant_id: str):
    """
    查询 saas slug 绑定信息
    """
    bind_info = get_bind_info(tenant_id)
    return bind_info


@api.post("/tenant/{tenant_id}/bind_saas/slug/", tags=['bind_saas'])
def set_bind_saas_slug(request, tenant_id: str):
    """
    设置 saas slug 绑定信息
    """
    tenant = Tenant.objects.get(id=tenant_id)
    bind_info = update_saas_binding(tenant, request.POST)
    create_arkidstore_login_app(tenant, bind_info['saas_tenant_slug'])
    create_arkid_saas_login_app(tenant, bind_info['saas_tenant_slug'])
    return bind_info


@api.get("/tenant/{tenant_id}/bind_saas/info/", tags=['bind_saas'], response=BindSaasInfoSchemaOut)
def get_bind_saas_info(request, tenant_id: str):
    """
    查询 saas info 绑定信息
    """
    bind_info = get_bind_info(tenant_id)
    return bind_info


@api.post("/tenant/{tenant_id}/bind_saas/info/", tags=['bind_saas'])
def update_bind_saas_info(request, tenant_id: str):
    """
    更新 saas info 绑定信息
    """
    tenant = Tenant.objects.get(id=tenant_id)
    bind_info = update_saas_binding(tenant, request.POST)
    create_arkidstore_login_app(tenant, bind_info['saas_tenant_slug'])
    create_arkid_saas_login_app(tenant, bind_info['saas_tenant_slug'])
    return bind_info


@api.post("/tenant/{tenant_id}/bind_saas/", tags=['bind_saas'])
def create_bind_saas(request, tenant_id: str):
    """
    检查slug是否存在的api
    发送 公司名,联系人,邮箱,手机号,Saas ArkID 租户slug
    本地租户绑定Saas租户
    """
    tenant = Tenant.objects.get(id=tenant_id)
    data = bind_saas(request.POST)
    return data

