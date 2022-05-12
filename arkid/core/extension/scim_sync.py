import requests
from types import SimpleNamespace
from typing import Literal, Union
from ninja import Schema
from pydantic import Field
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig
from arkid.core.extension import RootSchema, create_extension_schema
from pydantic import UUID4
from celery import shared_task
from arkid.common.logger import logger
from django.urls import reverse
from arkid.config import get_app_config
from scim_server.urls import urlpatterns as scim_server_urls
from django.urls import re_path
from scim_server.views.users_view import UsersViewTemplate
from scim_server.views.groups_view import GroupsViewTemplate
from scim_server.service.provider_base import ProviderBase
from scim_server.exceptions import NotImplementedException


class ScimSyncExtension(Extension, ProviderBase):
    TYPE = "scim_sync"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig

    @property
    def type(self):
        return ScimSyncExtension.TYPE

    def load(self):
        class UsersView(UsersViewTemplate):
            @property
            def provider(this):
                return self

        class GroupsView(GroupsViewTemplate):
            @property
            def provider(this):
                return self

        scim_server_urls = [
            re_path(
                rf'^scim/{self.name}/(?P<config_id>[\w-]+)/Users(?:/(?P<uuid>[^/]+))?$',
                UsersView.as_view(),
                name=f'{self.name}_scim_users',
            ),
            # re_path(r'^Groups/.search$', views.GroupSearchView.as_view(), name='groups-search'),
            re_path(
                rf'^scim/{self.name}/(?P<config_id>[\w-]+)/Groups(?:/(?P<uuid>[^/]+))?$',
                GroupsView.as_view(),
                name=f'{self.name}_scim_groups',
            ),
        ]
        self.register_routers(scim_server_urls, True)
        super().load()

    def register_scim_sync_schema(self, sync_type, client_schema, server_schema):
        schema = create_extension_schema(
            self.package,
            fields=[
                (
                    "__root__",
                    Union[(client_schema, server_schema)],
                    Field(discriminator="mode"),
                )
            ],
            base_schema=RootSchema,
        )
        self.register_config_schema(schema, self.package + '_' + sync_type)
        self.register_composite_config_schema(schema, sync_type, exclude=['extension'])

    def sync(self, config):
        logger.info(
            f"============= Sync Start With Config: {config}/{config.config} ================"
        )
        groups, users = self.get_groups_users(config)
        if not groups or not users:
            return
        self.sync_groups(groups, config)
        self.sync_users(users, config)

    def get_data(self, url):
        logger.info(f"Getting data from {url}")
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        return {}

    def get_groups_users(self, config):
        sync_server_id = config.config["sync_server_id"]
        server_config = TenantExtensionConfig.active_objects.filter(
            id=sync_server_id
        ).first()
        if not server_config:
            logger.error(f"No scim sync server config found: {sync_server_id}")
            return None, None
        group_url = server_config.config["group_url"]
        user_url = server_config.config["user_url"]
        groups = self.get_data(group_url).get("Resources")
        users = self.get_data(user_url).get("Resources")
        return groups, users

    @abstractmethod
    def sync_groups(self, groups, config):
        pass

    @abstractmethod
    def sync_users(self, users, config):
        pass

    def get_current_config(self, event):
        config_id = event.request.POST.get('config_id')
        return self.get_config_by_id(config_id)

    def create_tenant_config(self, tenant, config, name, type):
        config_created = super().create_tenant_config(
            tenant, config, name=name, type=type
        )
        if config["mode"] == "server":
            server_host = get_app_config().get_host()
            package = self.package.replace('.', '_')
            user_url = server_host + reverse(
                f'{package}:{self.name}_scim_users', args=[tenant.id, config_created.id]
            )
            group_url = server_host + reverse(
                f'{package}:{self.name}_scim_groups',
                args=[tenant.id, config_created.id],
            )
            config["group_url"] = group_url
            config["user_url"] = user_url
            config_created.config = config
            config_created.save()
        return config_created

    def create_user(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def create_group(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def delete_user(self, request, resource_identifier, correlation_identifier):
        raise NotImplementedException()

    def delete_group(self, request, resource_identifier, correlation_identifier):
        raise NotImplementedException()

    def replace_user(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def replace_group(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def retrieve_user(self, request, parameters, correlation_identifier):
        raise NotImplementedException()

    def retrieve_group(self, request, parameters, correlation_identifier):
        raise NotImplementedException()

    def update_user(self, request, patch, correlation_identifier):
        raise NotImplementedException()

    def update_group(self, request, patch, correlation_identifier):
        raise NotImplementedException()

    def query_users(self, request, parameters, correlation_identifier):
        pass

    def query_groups(self, request, parameters, correlation_identifier):
        pass


class BaseScimSyncClientSchema(Schema):
    # name: str = Field(default='', title=_('Name', '配置名称'))
    crontab: str = Field(default='0 1 * * *', title=_('Crontab', '定时运行时间'))
    max_retries: int = Field(default=3, title=_('Max Retries', '重试次数'))
    retry_delay: int = Field(default=60, title=_('Retry Delay', '重试间隔(单位秒)'))
    sync_server_name: str = Field(default="", title=_('Sync Server Name', '同步服务的名字'))
    sync_server_id: str = Field(
        default="", title=_('Sync Server ID', '同步服务的ID'), hidden=True
    )
    attr_map: dict = Field(default={}, title=_('Attribute Map', '同步映射关系'))
    mode: Literal["client"]


class BaseScimSyncServerSchema(Schema):
    # name: str = Field(title=_('配置名称'))
    mode: Literal["server"]
    user_url: str = Field(default="", title=_('User Url', '获取用户URL'))
    group_url: str = Field(default="", title=_('Group Url', '获取组URL'))