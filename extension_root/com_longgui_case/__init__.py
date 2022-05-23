from arkid.core import extension 
from arkid.core.translation import gettext_default as _
from arkid.core.models import User
from .models import CaseUser
from typing import List, Optional
from pydantic import Field

package = 'com.longgui.case'

UserSchema = extension.create_extension_schema(
    'UserSchema',
    package,
    fields=[
        ('username', str, Field()),
        ('nickname', Optional[str], Field()),
    ]
)

class CaseExtension(extension.Extension):
    def load(self):
        super().load()
        self.register_extend_field(CaseUser, 'nickname')
        self.register_api('/test/', 'POST', self.post_handler, auth=None, tenant_path=True)
        self.register_api('/test/', 'GET', self.get_handler, response=List[UserSchema], auth=None, tenant_path=True)

    def post_handler(self, request, tenant_id:str, data:UserSchema):
        tenant = request.tenant
        user = User()
        user.tenant = tenant
        user.username = data.username
        user.nickname = data.nickname
        user.save()

    def get_handler(self, request, tenant_id:str, ):
        users = User.expand_objects.filter(tenant=request.tenant).all()
        return list(users)
    
extension = CaseExtension(
    package=package,
    description="",
    version='1.0',
    labels='case',
    homepage='https://www.longguikeji.com',
    logo='',
    author='wely',
)