from abc import ABC, abstractmethod
from typing import Union, Literal, Any, List, Optional, Tuple, Type
from typing_extensions import Annotated
from pydantic import Field
from django.urls import include, re_path
from pathlib import Path

from requests import delete
from arkid import config
from types import SimpleNamespace
from collections import OrderedDict
from django.apps import apps
from django.conf import settings
from django.core import management
from arkid.core import api as core_api, pages as core_page, routers as core_routers, event as core_event
from arkid.core import urls as core_urls, expand as core_expand, models as core_models, translation as core_translation
from arkid.core.schema import RootSchema
from arkid.extension.models import TenantExtensionConfig, Extension as ExtensionModel, TenantExtension
from ninja import Schema
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja.orm import create_schema
from django.db.models import Model
from arkid.common.logger import logger
from arkid.core.models import EmptyModel


app_config = config.get_app_config()

Event = core_event.Event
EventType = core_event.EventType

def create_extension_schema( name, package = '', fields: Optional[List[Tuple[str, Any, Any]]] = None, base_schema:Type[Schema] = Schema) :
    """提供给插件用来创建Schema的方法
    
    注意:
        插件必须使用此方法来定义Schema,避免与其它Schema的命名冲突
    Args:
        name (str): Schema的类名
        package (str): 如果是插件调用的该方法,一定要将插件的package传过来,以避免命名冲突
        fields (Optional[List[Tuple[str, Any, Any]]], optional): Schema的字段定义
        base_schema (Type[Schema], optional): Schema的基类. 默认为: ninja.Schema
    Returns:
        ninja.Schema : 创建的Schema类
    """
    if package:
        name = package + '_' + name
    name = name.replace('.','_')
    schema = create_schema(EmptyModel,
            name=name, 
            exclude=['id'],
            custom_fields=fields,
            base_class=base_schema,
        )
    schema.name = name
    return schema


def create_extension_schema_from_django_model(
        model: Type[Model],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
        base_class: Type[Schema] = Schema,) :
    """提供给插件通过Django.Model创建Schema的方法
    注意:
        插件必须使用此方法来定义Schema,避免与其它Schema的命名冲突
        
    Args:
        model (Type[Model]): 基于的 Django Model
        name (str, optional): Schema的类名. 
        depth (int, optional): 遍历Django Model的深度. 
        fields (Optional[List[str]], optional): 从Django Model中获取的字段名, 如果是所有的就设为 \_\_all\_\_ . 
        exclude (Optional[List[str]], optional): 从Django Model中排除的字段名. 
        custom_fields (Optional[List[Tuple[str, Any, Any]]], optional): 添加的自定义字段. 
        base_class (Type[Schema], optional): Schema的基类. 
    Returns:
        ninjia.Schema: 新创建的Schema类
    """
    schema = create_schema(model=model, name=name, depth=depth,fields=fields, exclude=exclude, custom_fields=custom_fields, base_class=base_class)
    schema.name = name
    return schema

def create_empty_root_schema(name):
    return create_extension_schema(name, fields=[("__root__", str, Field())],base_schema=RootSchema,)

def get_root_schema(schema_list, discriminator, depth = 0):
    if len(schema_list) == 0:
        return Schema, Field()
    elif len(schema_list) == 1:
        return list(schema_list)[0],Field()
    else:
        return Union[tuple(schema_list)], Field(discriminator=discriminator, depth=depth)


extension_schema_map = {}
def create_config_schema_from_schema_list(schema_cls_name, schema_list, discriminator, depth = 0, **field_definitions):
    if len(schema_list) == 0:
        schema = create_extension_schema(schema_cls_name+'0')
    elif len(schema_list) == 1:
        # schema = list(schema_list)[0]
        schema = create_extension_schema(schema_cls_name+'1', base_schema=list(schema_list)[0])
    else:
        new_schema_list = []
        for schema in schema_list:
            schema = create_extension_schema(schema_cls_name + '_' + schema.name, base_schema=schema)
            core_api.add_fields(schema, **field_definitions)
            new_schema_list.append(schema)
            
        schema_list = new_schema_list
        root_type, root_field = Union[tuple(schema_list)], Field(discriminator=discriminator, depth=depth)
        
        schema = create_extension_schema(
            schema_cls_name, 
            fields=[
                ("__root__", root_type, root_field) # type: ignore
            ],
            base_schema=RootSchema,
        )
        extension_schema_map[schema_cls_name] = schema
    return schema


class Extension(ABC):
    """插件基类
    """
    extension_profile_schema_map = {}
    created_extension_profile_schema_list = []
    
    extension_settings_schema_map = {}
    created_extension_settings_schema_list = []
    
    extension_config_schema_map = {}
    created_extension_config_schema_list = []
    
    

    @property
    def type(self):
        return 'base'

    def __init__(self, package, version, description, labels, homepage, logo, author) -> None:
        self.package = package
        self.version = version
        self.description = description
        self.labels = labels
        self.homepage = homepage
        self.logo = logo
        self.author = author
        self.name = self.package.replace('.', '_')
        self.urls = []
        self.extend_fields = []
        self.events = []
        self.event_tags = []
        self.extend_apis = []
        self.front_routers = []
        self.front_pages = []
        self.profile_schema_list = []
        self.settings_schema_list = []
        self.config_schema_list = []
        self.lang_code = None

    @property
    def model(self):
        extension = ExtensionModel.valid_objects.filter(package=self.package).first()
        if not extension:
            raise Exception(f'cannot find {self.package} in database')
        else:
            return extension

    @property
    def ext_dir(self):
        return self._ext_dir

    @ext_dir.setter
    def ext_dir(self, value: str):
        self._ext_dir = value

    @property
    def full_name(self):
        return str(self.ext_dir).replace('/','.')

    def migrate_extension(self) -> None:
        extension_migrate_foldname = Path(self.ext_dir) / 'migrations'
        if not extension_migrate_foldname.exists():
            return
        settings.INSTALLED_APPS += (self.full_name, )
        apps.app_configs = OrderedDict()
        apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
        apps.clear_cache()
        apps.populate(settings.INSTALLED_APPS)

        # management.call_command('makemigrations', self.name, interactive=False)
        print(f'Migrate {self.name}')
        management.call_command('migrate', self.name, interactive=False)

    def register_routers(self, urls_ext, tenant_urls=False):
        if tenant_urls:
            urls_ext = [re_path(r'tenant/(?P<tenant_id>[\w-]+)/', include((urls_ext, 'extension'), namespace=f'{self.name}'))]
            self.urls.extend(urls_ext)
            core_urls.register(urls_ext)
        else:
            urls_ext = [re_path('', include((urls_ext, 'extension'), namespace=f'{self.name}'))]
            self.urls.extend(urls_ext)
            core_urls.register(urls_ext)

    def register_extend_field(self, model_cls, model_field, alias=None):
        if issubclass(model_cls, core_expand.TenantExpandAbstract):
            table = core_models.Tenant._meta.db_table
        elif issubclass(model_cls, core_expand.UserExpandAbstract):
            table = core_models.User._meta.db_table
        elif issubclass(model_cls, core_expand.UserGroupExpandAbstract):
            table = core_models.UserGroup._meta.db_table
        elif issubclass(model_cls, core_expand.AppExpandAbstract):
            table = core_models.App._meta.db_table
        elif issubclass(model_cls, core_expand.AppGroupExpandAbstract):
            table = core_models.AppGroup._meta.db_table
        elif issubclass(model_cls, core_expand.PermissionExpandAbstract):
            table = core_models.Permission._meta.db_table
        elif issubclass(model_cls, core_expand.ApproveExpandAbstract):
            table = core_models.Approve._meta.db_table
        elif issubclass(model_cls, core_expand.TenantConfigExpandAbstract):
            table = core_models.TenantConfig._meta.db_table
        else:
            raise Exception('非法的扩展字段类对应的父类')

        data = SimpleNamespace(
            table = table,
            field = alias or model_field,
            extension = self.name,
            extension_model_cls = model_cls,
            extension_table = model_cls._meta.db_table,
            extension_field = model_field,
        )

        self.extend_fields.append(data)
        core_expand.field_expand_map.append(data)

    def listen_event(self, tag, func):
        def signal_func(event, **kwargs2):
            # 判断租户是否启用该插件
            # tenant
            # 插件名 tag
            # func.__module__ 'extension_root.abc.xx'
            # kwargs2.pop()
            # Extension.
            if event.packages and not self.package in event.packages:
                return
            return func(event=event, **kwargs2)

        core_event.listen_event(tag, signal_func, listener=self)
        self.events.append((tag, signal_func))        

    def register_event(self, tag, name, data_schema=None, description=''):
        tag = self.package + '_' + tag
        core_event.register_event(tag, name, data_schema, description)
        self.event_tags.append(tag)
        return tag

    def dispatch_event(self, event):
        return core_event.dispatch_event(event=event, sender=self)

    def register_extend_api(self, api_schema_cls, **field_definitions):
        core_api.add_fields(api_schema_cls, **field_definitions)
        self.extend_apis.append((api_schema_cls, list(field_definitions.keys())))
        
    def register_languge(self, lang_code:str = 'en', lang_maps={}):
        self.lang_code = lang_code
        if lang_code in core_translation.extension_lang_maps.keys():
            core_translation.extension_lang_maps[lang_code][self.name] = lang_maps
        else:
            core_translation.extension_lang_maps[lang_code] = {}
            core_translation.extension_lang_maps[lang_code][self.name] = lang_maps
        core_translation.lang_maps = core_translation.reset_lang_maps()
        
    def register_front_routers(self, router, primary=''):
        """
        primary: 一级路由名字，由 core_routers 文件提供定义
        """
        router.path = self.package
        router.change_page_tag(self.package)

        for old_router, old_primary in self.front_routers:
            if old_primary == primary:
                self.front_routers.remove((old_router, old_primary))
                core_routers.unregister_front_routers(old_router, old_primary)

        core_routers.register_front_routers(router, primary)
        self.front_routers.append((router, primary))

    def register_front_pages(self, page):
        page:core_page.FrontPage
        page.add_tag_pre(self.package)

        core_page.register_front_pages(page)
        self.front_pages.append(page)

################################################################################
#### Base 
    
    def register_base_schema(self, schema, type, model, fields, schema_map, schema_list, schema_tag=None):
        schema_tag = schema_tag or self.package
        name = schema_tag.replace('.','_')+'_'+type
        new_schema = create_schema(model,
            name = name, 
            fields = fields,
            custom_fields=[
                ("package", Literal[schema_tag], Field()),  # type: ignore
                (type, schema, Field())
            ],
        )
        new_schema.name = name
        schema_map[schema_tag] = new_schema
        schema_list.append(schema_tag)

    @classmethod
    def create_base_schema(cls, name:str, created_schema_list:list, schema_map, **field_definitions):
        """创建并返回插件配置的Schema
        Args:
            name (str): 需要创建的 Schema Class 的名字
            created_schema_list (list): 列表，用于保存创建好的Schema
            field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
        """
        schema = create_empty_root_schema(name)
        cls.refresh_one_created_base_schema(schema, field_definitions, schema_map)
        created_schema_list.append( (schema,field_definitions) )
        return schema
        
    @classmethod
    def refresh_all_created_base_schema(cls, created_schema_list, schema_map):
        for schema,field_definitions in created_schema_list:
            cls.refresh_one_created_base_schema(schema, field_definitions, schema_map)
    
    @classmethod
    def refresh_one_created_base_schema(cls, schema, field_definitions, schema_map):
        temp_schema = create_config_schema_from_schema_list(schema.name+'_temp', schema_map.values(), 'package', **field_definitions)
        core_api.add_fields(schema, __root__=(temp_schema, Field()))

################################################################################

################################################################################
#### Profile 

    def register_profile_schema(self, schema, schema_tag=None):
        self.register_base_schema(
            schema, 'profile', ExtensionModel, 
            ['id','is_active','use_platform_config'],
            self.__class__.extension_profile_schema_map,
            self.profile_schema_list, schema_tag
        )

    @classmethod
    def create_profile_schema(cls, name:str, **field_definitions):
        """创建并返回插件配置的Schema
        Args:
            name (str): 需要创建的 Schema Class 的名字
            field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
        """
        return cls.create_base_schema(name, cls.created_extension_profile_schema_list, cls.extension_profile_schema_map, **field_definitions)
        
    @classmethod
    def refresh_all_created_profile_schema(cls):
        cls.refresh_all_created_base_schema(cls.created_extension_profile_schema_list, cls.extension_profile_schema_map)
    
################################################################################


################################################################################
#### Settings 

    def register_settings_schema(self, schema, schema_tag=None):
        self.register_base_schema(
            schema, 'settings', TenantExtension, 
            ['id','is_active','use_platform_config'],
            self.__class__.extension_settings_schema_map,
            self.settings_schema_list, schema_tag
        )

    @classmethod
    def create_settings_schema(cls, name:str, **field_definitions):
        """创建并返回插件 租户配置(settings) 的Schema
        Args:
            name (str): 需要创建的 Schema Class 的名字
            field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
        """
        return cls.create_base_schema(name, cls.created_extension_settings_schema_list, cls.extension_settings_schema_map, **field_definitions)
        
    @classmethod
    def refresh_all_created_settings_schema(cls):
        cls.refresh_all_created_base_schema(cls.created_extension_settings_schema_list, cls.extension_settings_schema_map)

    def get_tenant_settings(self, tenant):
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        settings = TenantExtension.valid_objects.filter(tenant=tenant, extension=ext).first()
        return settings

    def create_tenant_settings(self, tenant, settings):
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        return TenantExtension.objects.create(tenant=tenant, extension=ext, settings=settings)
    
################################################################################

################################################################################
#### Config 
    
    def register_config_schema(self, schema, schema_tag=None):
        self.register_base_schema(
            schema, 'config', TenantExtensionConfig, 
            ['id','name'],
            self.__class__.extension_config_schema_map,
            self.config_schema_list, schema_tag
        )

    @classmethod
    def create_config_schema(cls, name:str, **field_definitions):
        """创建并返回插件 运行时配置 的Schema
        Args:
            name (str): 需要创建的 Schema Class 的名字
            field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
        """
        return cls.create_base_schema(name, cls.created_extension_config_schema_list, cls.extension_config_schema_map, **field_definitions)
        
    @classmethod
    def refresh_all_created_config_schema(cls):
        cls.refresh_all_created_base_schema(cls.created_extension_config_schema_list, cls.extension_config_schema_map)
        
    def get_tenant_configs(self, tenant):
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        configs = TenantExtensionConfig.valid_objects.filter(tenant=tenant, extension=ext).all()
        return configs

    def get_config_by_id(self, id):
        return TenantExtensionConfig.valid_objects.get(id=id)
    
    def update_tenant_config(self, id,  config, name):
        return TenantExtensionConfig.valid_objects.filter(id=id).update(config=config, name=name)

    def create_tenant_config(self, tenant, config, name):
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        return TenantExtensionConfig.objects.create(tenant=tenant, extension=ext, config=config, name=name)
    
    def delete_tenant_config(self, tenant, config):
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        return TenantExtensionConfig.objects.delete(tenant=tenant, extension=ext, config=config)

################################################################################


################################################################################
#### Composite Config 

    def register_composite_config_schema(self, schema, composite_value, exclude=[], package=None):
        package = package or self.package
        exclude.extend(['is_del', 'is_active', 'updated', 'created', 'tenant'])
        name = package + '_' + composite_value + '_config'
        new_schema = create_schema(self.__class__.composite_model,
            name=name,
            exclude=exclude,
            custom_fields=[
                (self.__class__.composite_key, Literal[composite_value], Field()), # type: ignore
                ("package", Literal[package], Field()), # type: ignore
                ("config", schema, Field()),
            ],
        )
        new_schema.name = name
        if composite_value not in self.__class__.composite_schema_map:
            self.composite_schema_map[composite_value] = {}
        self.composite_schema_map[composite_value][package] = new_schema
    
    @classmethod
    def create_composite_config_schema(cls, schema_cls_name, **field_definitions):
        schema = create_extension_schema(
            schema_cls_name, 
            fields=[
                ("__root__", str, Field(depth=1)) # type: ignore
            ],
            base_schema=RootSchema,
        )
        cls.created_composite_schema_list.append((schema, field_definitions))
        cls.refresh_all_created_composite_schema()
        return schema
    
    @classmethod
    def refresh_all_created_composite_schema(cls):
        if not hasattr(cls, "created_composite_schema_list"):
            return
        for created_ext_config_schema, field_definitions in cls.created_composite_schema_list:
            temp_list = {}
            for composite_key, package_schema_map in cls.composite_schema_map.items():
                schema_name = created_ext_config_schema.name + composite_key
                new_schema = create_config_schema_from_schema_list(
                    schema_name, 
                    package_schema_map.values(),
                    'package',
                    **field_definitions,
                )
                temp_list[composite_key] = new_schema
            

            root_type, root_field = get_root_schema(temp_list.values(), cls.composite_key, depth=1)
            core_api.add_fields(created_ext_config_schema, __root__=(root_type, root_field))
            
################################################################################


    

    @abstractmethod
    def load(self):
        pass

    def start(self):
        try:
            self.migrate_extension()
        except Exception as e:
            print(e)
            logger.error(e)
        self.load()
        self.__class__.refresh_all_created_profile_schema()
        self.__class__.refresh_all_created_settings_schema()
        self.__class__.refresh_all_created_config_schema()
        self.__class__.refresh_all_created_composite_schema()
        
        # self.install_requirements() sys.modeles

    def unload(self):
        core_urls.unregister(self.urls)
        for tag, func in self.events:
            core_event.unlisten_event(tag, func)
        for field in self.extend_fields:
            core_expand.field_expand_map.remove(field)
        for api_schema_cls, fields in self.extend_apis:
            core_api.remove_fields(api_schema_cls, fields)
        for old_router, old_primary in self.front_routers:
            core_routers.unregister_front_routers(old_router, old_primary)
        for page in self.front_pages:
            core_page.unregister_front_pages(page)
        for tag in self.event_tags:
            core_event.unregister_event(tag)
        for schema_tag in self.profile_schema_list:
            self.__class__.extension_profile_schema_map.pop(schema_tag, None)
        self.__class__.refresh_all_created_profile_schema()
        for schema_tag in self.settings_schema_list:
            self.__class__.extension_settings_schema_map.pop(schema_tag, None)
        self.__class__.refresh_all_created_settings_schema()
        for schema_tag in self.config_schema_list:
            self.__class__.extension_config_schema_map.pop(schema_tag, None)
        self.__class__.refresh_all_created_config_schema()
        
        delete_ks = []
        for k,v in self.__class__.composite_schema_map.items():
            v.pop(self.package, None)
            if not self.__class__.composite_schema_map[k]:
                delete_ks.append(k)
        for k in delete_ks:
            self.__class__.composite_schema_map.pop(k)
        self.__class__.refresh_all_created_composite_schema()

        if self.lang_code:
            core_translation.extension_lang_maps[self.lang_code].pop(self.name)
            if not core_translation.extension_lang_maps[self.lang_code]:
                core_translation.extension_lang_maps.pop(self.lang_code)
            core_translation.lang_maps = core_translation.reset_lang_maps()
            
        self.urls = []
        self.extend_fields = []
        self.events = []
        self.event_tags = []
        self.extend_apis = []
        self.front_routers = []
        self.front_pages = []
        self.profile_schema_list = []
        self.settings_schema_list = []
        self.config_schema_list = []