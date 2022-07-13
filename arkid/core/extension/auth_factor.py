
from ninja import Schema
from pydantic import Field
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.core.event import Event, dispatch_event
from arkid.extension.models import TenantExtensionConfig
from arkid.common.logger import logger
from arkid.core.models import User


class AuthFactorExtension(Extension):
    
    TYPE = "auth_factor"
    
    
    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig
    
    @property
    def type(self):
        return AuthFactorExtension.TYPE
    
    LOGIN = 'login'
    REGISTER = 'register'
    RESET_PASSWORD = 'password'

    def register_user_key_fields(self, **fields):
        User.register_key_field(**fields)
    
    def load(self):
        super().load()
        
        self.listen_events()
        
        self.register_auth_manage_page()

    def register_auth_factor_schema(self, schema, auth_factor_type):
        self.register_config_schema(schema, self.package + '_' + auth_factor_type)
        self.register_composite_config_schema(schema, auth_factor_type, exclude=['extension'])
    
    def start_authenticate(self,event,**kwargs):
        config = self.get_current_config(event)
        dispatch_event(Event(tag=core_event.BEFORE_AUTH, tenant=event.tenant, request=event.request, data={"auth_factor_config":config}))
        return self.authenticate(event, **kwargs)

    @abstractmethod
    def authenticate(self, event, **kwargs):
        pass

    def auth_success(self, user, event, **kwargs):
        config = self.get_current_config(event)
        dispatch_event(Event(tag=core_event.AUTH_SUCCESS, tenant=event.tenant, request=event.request, data={"auth_factor_config":config}))
        return user
    
    def auth_failed(self, event, data, **kwargs):
        config = self.get_current_config(event)
        dispatch_event(Event(tag=core_event.AUTH_FAIL, tenant=event.tenant, request=event.request,  data={"auth_factor_config_id":config.id.hex,"data":data}))
        core_event.remove_event_id(event)
        core_event.break_event_loop(data)

    @abstractmethod
    def register(self, event, **kwargs):
        pass
    
    @abstractmethod
    def reset_password(self, event, **kwargs):
        pass
    
    def create_response(self, event, **kwargs):
        logger.info(f'{self.package} create_response start')
        self.data = {}
        configs = self.get_tenant_configs(event.tenant)
        for config in configs:
            
            config_data = {
                self.LOGIN: {
                    'forms':[],
                    'bottoms':[],
                    'expand':{},
                },
                self.REGISTER: {
                    'forms':[],
                    'bottoms':[],
                    'expand':{},
                },
                self.RESET_PASSWORD: {
                    'forms':[],
                    'bottoms':[],
                    'expand':{},
                },
            }
            
            if config.config.get("login_enabled", True):
                self.create_login_page(event,config,config_data)
            if config.config.get("register_enabled", True):
                self.create_register_page(event, config,config_data)
            if config.config.get("reset_password_enabled", True):
                self.create_password_page(event, config,config_data)
            self.create_other_page(event, config, config_data)
            self.data[config.id.hex] = config_data
        logger.info(self.data)
        logger.info(f'{self.package} create_response end')
        return self.data
        
    def add_page_form(self, config, page_name, label, items, config_data, submit_url=None, submit_label=None):
        default = {
            "login": ("登录", f"/api/v1/tenant/tenant_id/auth/?event_tag={self.auth_event_tag}"),
            "register": ("登录", f"/api/v1/tenant/tenant_id/register/?event_tag={self.register_event_tag}"),
            "password": ("登录", f"/api/v1/tenant/tenant_id/reset_password/?event_tag={self.password_event_tag}"),
        }
        if not submit_label:
            submit_label, useless = default.get(page_name)
        if not submit_url:
            useless, submit_url = default.get(page_name)

        items.append({"type": "hidden", "name": "config_id", "value": config.id})
        config_data[page_name]['forms'].append({
            'label': label,
            'items': items,
            'submit': {'label': submit_label, 'http': {'url': submit_url, 'method': "post"}}
        })

    def add_page_bottoms(self, page_name, bottoms):
        self.data[page_name]['bottoms'].append(bottoms)

    def add_page_extend(self, page_name, buttons, title=None):
        if not self.data[page_name].get('extend'):
            self.data[page_name]['extend'] = {}

        self.data[page_name]['extend']['title'] = title
        self.data[page_name]['extend']['buttons'].append(buttons)

    @abstractmethod
    def create_login_page(self, event, config, config_data):
        pass

    @abstractmethod
    def create_register_page(self, event, config, config_data):
        pass

    @abstractmethod
    def create_password_page(self, event, config, config_data):
        pass

    @abstractmethod
    def create_other_page(self, event, config, config_data):
        pass
    
    def register_auth_manage_page(self):
        from api.v1.pages.mine.auth_manage import page as auth_manage_page
        pages = self.create_auth_manage_page()
        
        if not pages:
            return
        
        if not isinstance(pages,list):
            pages = [pages]
        for page in pages:
            self.register_front_pages(page)
            auth_manage_page.add_pages(page)
    
    @abstractmethod
    def create_auth_manage_page(self):
        pass
    
    def fix_login_page(self, event, **kwargs):
        pass
    
    def get_current_config(self, event):
        config_id = event.request.POST.get('config_id')
        return self.get_config_by_id(config_id)

    def listen_events(self):
        self.auth_event_tag = self.register_event('auth', '认证')
        self.listen_event(self.auth_event_tag, self.start_authenticate)
        self.register_event_tag = self.register_event('register', '注册')
        self.listen_event(self.register_event_tag, self.register)
        self.password_event_tag = self.register_event('password', '重置密码')
        self.listen_event(self.password_event_tag, self.reset_password)
        self.listen_event(core_event.CREATE_LOGIN_PAGE_AUTH_FACTOR, self.create_response)
        
        self.listen_event(core_event.AUTHRULE_FIX_LOGIN_PAGE,self.fix_login_page)

class BaseAuthFactorSchema(Schema):
    login_enabled: bool = Field(default=True, title=_('login_enabled', '启用登录'))
    register_enabled: bool = Field(default=True, title=_('register_enabled', '启用注册'))
    reset_password_enabled: bool = Field(default=True, title=_('reset_password_enabled', '启用重置密码'))
