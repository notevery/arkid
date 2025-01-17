from enum import Enum
from typing import Any, Dict, Optional, List
from ninja import Schema, Query, ModelSchema
from arkid.core.event import register_event, dispatch_event, Event, USER_REGISTER
from arkid.core.api import api, operation
from arkid.core.models import Tenant, ExpiringToken, User
from arkid.core.translation import gettext_default as _
from arkid.core.token import refresh_token
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.schema import ResponseSchema, UserSchemaOut


class RegisterTenantSchema(ModelSchema):
    class Config:
        model = Tenant
        model_fields = ['id', 'name', 'slug', 'icon']
        # validate = False


class RegisterDataOut(Schema):
    user: UserSchemaOut
    token: str


class RegisterOut(ResponseSchema):
    data: Optional[RegisterDataOut]


@api.post("/tenant/{tenant_id}/register/", response=RegisterOut, tags=['登录与注册'], auth=None)
@operation(RegisterOut, use_id=True)
def register(request, tenant_id: str, event_tag: str):
    tenant = request.tenant
    request_id = request.META.get('request_id')

    # 认证
    responses = dispatch_event(Event(tag=event_tag, tenant=tenant, request=request, uuid=request_id))
    if len(responses) < 1:
        return {'error': 'error_code', 'message': '认证插件未启用'}

    useless, (user, useless) = responses[0]

    # 此处临时判断注册返回结果是否为User对象
    if isinstance(user,User):
        # 用户注册和登录
        dispatch_event(Event(tag=USER_REGISTER, tenant=tenant, request=request, data=user))

        # 生成 token
        token = refresh_token(user)

        return {'error': ErrorCode.OK.value, 'data': {'user': user, 'token': token}}
    else:
        return user
