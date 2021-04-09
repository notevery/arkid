from typing import Dict
from .user_info_manager import GithubUserInfoManager
from common.provider import ExternalIdpProvider
from .constants import KEY, BIND_KEY, LOGIN_URL, IMG_URL
from django.urls import reverse


class GithubExternalIdpProvider(ExternalIdpProvider):

    bind_key: str = BIND_KEY
    name: str

    client_id: str
    secret_id: str

    def __init__(self) -> None:
        super().__init__()

    def load_data(self, tenant_uuid):
        from tenant.models import Tenant
        from external_idp.models import ExternalIdp

        idp = ExternalIdp.objects.filter(
            tenant__uuid=tenant_uuid,
            type=KEY,
        ).first()

        data = idp.data

        client_id = data.get('client_id')
        secret_id = data.get('secret_id')

        self.client_id = client_id
        self.secret_id = secret_id

    def create(self, tenant_uuid, external_idp, data):
        client_id = data.get('client_id')
        secret_id = data.get('secret_id')

        return {
            'client_id': client_id,
            'secret_id': secret_id,
            'login_url': reverse("api:github:login", args=[tenant_uuid]),
            'callback_url' : reverse("api:github:callback", args=[tenant_uuid]),
            'bind_url' : reverse("api:github:bind", args=[tenant_uuid]),
            'img_url': IMG_URL,
        }

    def bind(self, user: any, data: Dict):
        from .models import GithubUser

        GithubUser.objects.get_or_create(
            tenant=user.tenant,
            user=user,
            github_user_id=data.get('user_id'),
        )