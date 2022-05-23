
from django.http import JsonResponse
from collections import OrderedDict
from arkid.core.models import Tenant
from arkid.core.error import ErrorCode
from arkid.common.arkstore import (
    get_arkstore_access_token,
    purcharse_arkstore_extension,
    lease_arkstore_extension,
    install_arkstore_extension,
    get_arkstore_apps,
    get_arkstore_extensions,
    get_arkid_saas_app_detail,
    get_bind_arkstore_agent,
    bind_arkstore_agent,
    change_arkstore_agent,
    unbind_arkstore_agent
)
from arkid.core.api import api
from typing import List
from ninja import Schema
from pydantic import Field
from ninja.pagination import paginate


def get_arkstore_list(request, purchased, type):
    page = request.GET.get('page')
    page_size = request.GET.get('page_size')
    purchased = True
    token = request.user.auth_token
    tenant = request.tenant
    access_token = get_arkstore_access_token(tenant, token.token)
    # arkstore use offset and limit
    if page and page_size:
        limit = int(page_size)
        offset = (int(page)-1) * int(page_size)
        saas_extensions_data = get_arkstore_extensions(access_token, purchased, offset, limit)
    else:
        saas_extensions_data = get_arkstore_extensions(access_token, purchased)
    saas_extensions_data = saas_extensions_data['items']
    saas_extensions = []
    for extension in saas_extensions_data:
        if extension['upgrade']:
            extension['button'] = '升级'
        elif extension['purchased']:
            extension['button'] = '安装'
        else:
            extension['button'] = '购买'
        saas_extensions.append(extension)

    return saas_extensions


class ArkstoreItemSchemaOut(Schema):
    uuid: str = Field(hidden=True)
    name: str
    package_idendifer: str
    version: str
    author: str
    logo: str = ""
    description: str
    categories: str
    labels: str
    button: str


class BindAgentSchemaIn(Schema):
    tenant_slug: str


@api.get("/tenant/{tenant_id}/arkstore/extensions/", tags=['arkstore'], response=List[ArkstoreItemSchemaOut])
@paginate
def list_arkstore_extensions(request, tenant_id: str):
    return get_arkstore_list(request, None, 'extension')

@api.get("/tenant/{tenant_id}/arkstore/apps/", tags=['arkstore'], response=List[ArkstoreItemSchemaOut])
@paginate
def list_arkstore_apps(request, tenant_id: str):
    return get_arkstore_list(request, None, 'app')


@api.get("/tenant/{tenant_id}/arkstore/purchased/extensions/", tags=['arkstore'], response=List[ArkstoreItemSchemaOut])
@paginate
def list_arkstore_purchased_extensions(request, tenant_id: str):
    return get_arkstore_list(request, True, 'extension')


@api.get("/tenant/{tenant_id}/arkstore/purchased/apps/", tags=['arkstore'], response=List[ArkstoreItemSchemaOut])
@paginate
def list_arkstore_purchased_apps(request, tenant_id: str):
    return get_arkstore_list(request, True, 'app')


@api.post("/tenant/{tenant_id}/arkstore/purchase/{uuid}/", tags=['arkstore'])
def order_arkstore_extension(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = purcharse_arkstore_extension(access_token, uuid)
    return resp


@api.get("/tenant/{tenant_id}/arkstore/lease/{uuid}/", tags=['arkstore'])
def rent_arkstore_extension(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    # platform_tenant = Tenant.objects.filter(slug='').first()
    # saas_token, saas_tenant_id, saas_tenant_slug = get_saas_token(platform_tenant, token)
    access_token = get_arkstore_access_token(tenant, token)
    # bind_arkstore_agent(access_token, saas_tenant_slug)
    resp = lease_arkstore_extension(access_token, uuid)
    return resp


@api.get("/tenant/{tenant_id}/arkstore/install/{uuid}/", tags=['arkstore'])
def download_arkstore_extension(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    result = install_arkstore_extension(tenant, token, uuid)
    resp = {'error': ErrorCode.OK.value}
    return resp


@api.get("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['arkstore'])
def get_arkstore_bind_agent(request, tenant_id: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = get_bind_arkstore_agent(access_token)
    return resp


@api.post("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['arkstore'])
def create_arkstore_bind_agent(request, tenant_id: str, data: BindAgentSchemaIn):
    tenant_slug = data.tenant_slug
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = bind_arkstore_agent(access_token, tenant_slug)
    return resp


@api.delete("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['arkstore'])
def delete_arkstore_bind_agent(request, tenant_id: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = unbind_arkstore_agent(access_token)
    return resp


@api.put("/tenant/{tenant_id}/arkstore/bind_agent/", tags=['arkstore'])
def update_arkstore_bind_agent(request, tenant_id: str, data: BindAgentSchemaIn):
    tenant_slug = data.tenant_slug
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    access_token = get_arkstore_access_token(tenant, token)
    resp = change_arkstore_agent(access_token, tenant_slug)
    return resp


@api.get("/tenant/{tenant_id}/arkstore/auto_fill_form/{uuid}/", tags=['arkstore'])
def get_arkstore_app(request, tenant_id: str, uuid: str):
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    resp = get_arkid_saas_app_detail(tenant, token, uuid)
    return resp
