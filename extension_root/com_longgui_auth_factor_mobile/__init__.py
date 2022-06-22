from arkid.core.api import operation
from arkid.core.event import SEND_SMS, Event, dispatch_event
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.common.logger import logger
from arkid.extension.models import TenantExtensionConfig
from .error import ErrorCode
from arkid.core.models import User
from .sms import check_sms_code, create_sms_code,gen_sms_code
from arkid.core import actions, pages
from .models import UserMobile
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.db import transaction
from arkid.core.extension import create_extension_schema
from .schema import *
from django.contrib.auth.hashers import (
    make_password,
)

package = "com.longgui.auth.factor.mobile"

class MobileAuthFactorExtension(AuthFactorExtension):
    
    send_sms_code_path:str = ""
    
    def load(self):
        super().load()
        
        self.create_extension_config_schema()
        
        self.register_extend_field(UserMobile, "mobile")
        from api.v1.schema.auth import AuthIn
        from api.v1.schema.user import UserCreateIn,UserItemOut,UserUpdateIn,UserListItemOut
        from api.v1.schema.mine import ProfileSchemaOut
        self.register_extend_api(
            AuthIn,
            UserCreateIn, 
            UserItemOut, 
            UserUpdateIn, 
            UserListItemOut,
            mobile=(Optional[str],Field(title=_("电话号码"))),
            # areacode=(str,Field(title=_("区号")))
        )
        self.register_extend_api(
            ProfileSchemaOut, 
            mobile=(Optional[str],Field(readonly=True))
        )
        
        # 注册发送短信接口
        self.send_sms_code_path = self.register_api(
            '/send_sms_code/',
            'POST',
            self.send_sms_code,
            tenant_path=True,
            auth=None,
            response=SendSMSCodeOut,
        )
    
    def authenticate(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        sms_code = request.POST.get('sms_code')
        mobile = request.POST.get('mobile')

        user = User.expand_objects.filter(tenant=tenant,mobile=mobile)
        if len(user) > 1:
            logger.error(f'{mobile}在数据库中匹配到多个用户')
            return self.auth_failed(event, data=self.error(ErrorCode.CONTACT_MANAGER))
        if user:
            user = user[0]
            if check_sms_code(mobile, sms_code):
                user = User.active_objects.get(id=user.get("id"))
                return self.auth_success(user,event)
            else:
                msg = ErrorCode.SMS_CODE_MISMATCH
        else:
            msg = ErrorCode.MOBILE_NOT_EXISTS_ERROR
        return self.auth_failed(event, data=self.error(msg))

    @transaction.atomic()
    def register(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')

        config = self.get_current_config(event)
        ret, message = self.check_mobile_exists(mobile, config)
        if not ret:
            return self.error(message)
        
        if not check_sms_code(mobile, sms_code):
            return self.error(ErrorCode.SMS_CODE_MISMATCH)
        
        user = User(tenant=tenant)

        user.mobile = mobile
        user.username = mobile
        
        user.save()
        tenant.users.add(user)
        tenant.save()

        return user

    def reset_password(self, event, **kwargs):
        print(event)
        tenant = event.tenant
        request = event.request
        mobile = request.POST.get('mobile')
        sms_code = request.POST.get('sms_code')
        
        password = request.POST.get('password')
        checkpassword = request.POST.get('checkpassword')
        
        if password != checkpassword:
            return self.error(ErrorCode.PASSWORD_IS_INCONSISTENT)
                
        if not check_sms_code(mobile, sms_code):
            return self.error(ErrorCode.SMS_CODE_MISMATCH)
        
        user = User.expand_objects.filter(tenant=tenant,mobile=mobile)
        
        if len(user) > 1:
            logger.error(f'{mobile}在数据库中匹配到多个用户')
            return self.error(ErrorCode.CONTACT_MANAGER)
        if user:
            user = user[0]
            user = User.active_objects.get(id=user.get("id"))
            user.password = make_password(password)
            user.save()
            return self.success()
        
        return self.error(ErrorCode.MOBILE_NOT_EXISTS_ERROR)

    def create_login_page(self, event, config):
        items = [
            {
                "type": "text",
                "title":"mobile",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.send_sms_code_path,
                        "method": "post",
                        "params": {
                            "mobile": "mobile",
                            "config_id": config.id,
                            "areacode": "86",
                            "package": config.id
                        },
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "title":"sms_code",
                "placeholder": "验证码",
            },
        ]
        self.add_page_form(config, self.LOGIN, "手机验证码登录", items)

    def create_register_page(self, event, config):
        items = [
            {
                "type": "text",
                "title":"mobile",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.send_sms_code_path,
                        "method": "post",
                        "params": {
                            "mobile": "mobile",
                            "config_id": config.id,
                            "areacode": "86",
                            "package": self.package
                        },
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "title":"sms_code",
                "placeholder": "验证码"
            },
        ]
        self.add_page_form(config, self.REGISTER, "手机验证码注册", items)

    def create_password_page(self, event, config):
        items = [
            {
                "type": "text",
                "title":"mobile",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.send_sms_code_path,
                        "method": "post",
                        "params": {
                            "mobile": "mobile",
                            "config_id": config.id,
                            "areacode": "86",
                            "package": self.package
                        },
                    },
                }
            },
            {
                "type": "text",
                "title":"sms_code",
                "placeholder": "验证码"
            },
            {
                "type": "password",
                "title":"password",
                "placeholder": "密码"
            },
            {
                "type": "password",
                "title":"checkpassword",
                "placeholder": "密码确认"
            },
        ]
        self.add_page_form(config, self.RESET_PASSWORD, "手机验证码重置密码", items)

    def create_other_page(self, event, config):
        pass
    
    def check_mobile_exists(self, mobile, config):
        if not mobile:
            return False, ErrorCode.MOBILE_EMPTY

        if UserMobile.active_objects.filter(mobile=mobile).count():
            return False, ErrorCode.MOBILE_EXISTS_ERROR
        return True, None

    def _get_register_user(self, tenant, field_name, field_value):
        pass
    
    def create_auth_manage_page(self):

        configs = TenantExtensionConfig.active_objects.filter(extension__package=self.package)
        
        for config in configs:
            class UpdateMineMobileIn(Schema):
                    
                modile:str = Field(
                    title='手机号',
                    suffix_action=DirectAction(
                        name='发送验证码',
                        path=self.send_sms_code_path,
                        method=actions.FrontActionMethod.POST,
                        params={
                            "mobile": "mobile",
                            "config_id": config.id,
                            "areacode": "86",
                            "package": self.package
                        },
                        delay=60,
                    ).dict()
                )
                
                code:str = Field(title='验证码')
            
            class UpdateMineMobileOut(ResponseSchema):
                pass
            
            def update_mine_mobile(request, tenant_id: str,data:UpdateMineMobileIn):
                return self.success()
        
            
            mine_mobile_path = self.register_api(
                "/mine_mobile/",
                'POST',
                update_mine_mobile,
                tenant_path=True,
                response=UpdateMineMobileOut
            )
            
            name = '更改手机号码'

            page = pages.FormPage(name=name)
            page.create_actions(
                init_action=actions.ConfirmAction(
                    path=mine_mobile_path
                ),
                global_actions={
                    'confirm': actions.ConfirmAction(
                        path=mine_mobile_path
                    ),
                }
            )
            return page

    def create_extension_config_schema(self):
        
        select_sms_page = pages.TablePage(select=True,name=_("指定短信插件运行时"))

        self.register_front_pages(select_sms_page)

        select_sms_page.create_actions(
            init_action=actions.DirectAction(
                path='/api/v1/tenants/{tenant_id}/config_select/?extension__type=sms',
                method=actions.FrontActionMethod.GET
            )
        )
        
        MobileAuthFactorSchema = create_extension_schema(
            'MobileAuthFactorSchema',
            package, 
            [
                (
                    'sms_config', 
                    MobileAuthFactorConfigSchema, 
                    Field(
                        title=_('sms extension config', '短信插件运行时'),
                        page=select_sms_page.tag,
                    )
                ),
            ],
            BaseAuthFactorSchema,
        )
        self.register_auth_factor_schema(MobileAuthFactorSchema, 'mobile')
    
    @operation(SendSMSCodeOut)
    def send_sms_code(self,request,tenant_id,data:SendSMSCodeIn):
        """发送短信验证码

        Args:
            request : 请求对象
            tenant_id (str): 租户ID
            data (SendSMSCodeIn): 参数体
        """
        tenant = request.tenant
        code = create_sms_code(data.mobile)
        print(code)
        mobile = data.mobile
        if not mobile or mobile=="mobile":
            return self.error(ErrorCode.MOBILE_EMPTY)
        
        responses = dispatch_event(
            Event(
                tag=SEND_SMS,
                tenant=tenant,
                request=request,
                data={
                    "config_id":data.config_id,
                    "mobile":data.mobile,
                    "code": code,
                    "areacode": data.areacode
                },
                packages=[
                    data.package
                ]
            )
        )
        
        if not responses:
            return self.error(ErrorCode.SMS_EXTENSION_NOT_EXISTS)
        useless, (data, extension) = responses[0]
        if data:
            return self.success()
        else:
            return self.error(ErrorCode.SMS_SEND_FAILED)
        
extension = MobileAuthFactorExtension(
    package=package,
    name="手机验证码认证因素",
    version='1.0',
    labels='auth_factor',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)