from .base import BaseViewSet
from api.v1.serializers.other_auth_factor import (
    OtherAuthFactorSerializer,
    OtherAuthFactorListSerializer,
)
from runtime import get_app_runtime
from django.http.response import JsonResponse
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from login_register_config.models import OtherAuthFactor
from rest_framework.decorators import action
from perm.custom_access import ApiAccessPermission
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from common.code import Code
from drf_spectacular.utils import extend_schema_view, OpenApiParameter
from tenant.models import Tenant

OtherAuthFactorPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='OtherAuthFactorPolymorphicProxySerializer',
    serializers=get_app_runtime().other_auth_factor_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    destroy=extend_schema(roles=['tenantadmin', 'globaladmin', 'authfactor.otherauthfactor'], summary='删除其它认证因素'),
    partial_update=extend_schema(roles=['tenantadmin', 'globaladmin', 'authfactor.otherauthfactor'], summary='批量修改其它认证因素'),
)
@extend_schema(
    tags=['other_auth_factor'],
    roles=['tenantadmin', 'globaladmin'],
    parameters=[
        OpenApiParameter(
            name='tenant',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
)
class OtherAuthFactorViewSet(BaseViewSet):

    model = OtherAuthFactor

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = OtherAuthFactorSerializer

    def get_queryset(self):

        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        kwargs = {
            'tenant': tenant,
        }

        return OtherAuthFactor.valid_objects.filter(**kwargs)

    def get_object(self):
        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = OtherAuthFactor.valid_objects.filter(**kwargs).first()
        return obj

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.otherauthfactor'],
        responses=OtherAuthFactorListSerializer,
        summary='其它认证因素列表'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.otherauthfactor'],
        request=OtherAuthFactorPolymorphicProxySerializer,
        responses=OtherAuthFactorPolymorphicProxySerializer,
        summary='其它认证因素修改'
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.otherauthfactor'],
        request=OtherAuthFactorPolymorphicProxySerializer,
        responses=OtherAuthFactorPolymorphicProxySerializer,
        summary='其它认证因素创建'
    )
    def create(self, request, *args, **kwargs):
        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.otherauthfactor'],
        responses=OtherAuthFactorPolymorphicProxySerializer,
        summary='其它认证因素获取'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)