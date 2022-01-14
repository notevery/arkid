from typing import Dict
from .user_info_manager import WeChatWorkScanUserInfoManager
from common.provider import ExternalIdpProvider
from .constants import KEY, IMG_URL
from django.urls import reverse
from config import get_app_config


class WeChatWorkScanExternalIdpProvider(ExternalIdpProvider):

    agentid: str
    corpid: str
    corpsecret: str
    login_url: str
    bind_url: str
    userinfo_url: str

    def __init__(self) -> None:
        super().__init__()

    def load_data(self, tenant_uuid):
        from tenant.models import Tenant
        from external_idp.models import ExternalIdp
        host = get_app_config().get_host()

        idp = ExternalIdp.active_objects.filter(
            tenant__uuid=tenant_uuid,
            type=KEY,
        ).first()

        assert idp is not None
        data = idp.data

        agentid = data.get('agentid')
        corpid = data.get('corpid')
        corpsecret = data.get('corpsecret')
        bind_url = data.get('bind_url')
        userinfo_url = data.get('userinfo_url')

        self.agentid = agentid
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.bind_url = bind_url
        self.userinfo_url = userinfo_url

    def create(self, tenant_uuid, external_idp, data):
        host = get_app_config().get_host()
        agentid = data.get('agentid')
        corpid = data.get('corpid')
        corpsecret = data.get('corpsecret')
        login_url = host+reverse("api:wechatworkscan:login", args=[tenant_uuid])
        bind_url = host+reverse("api:wechatworkscan:bind", args=[tenant_uuid])
        userinfo_url = host+reverse("api:wechatworkscan:userinfo", args=[tenant_uuid])

        return {
            'agentid': agentid,
            'corpid': corpid,
            'corpsecret': corpsecret,
            'login_url': login_url,
            'bind_url': bind_url,
            'userinfo_url': userinfo_url,
            'img_url': IMG_URL,
        }
