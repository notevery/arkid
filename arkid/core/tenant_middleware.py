import re
import json
from django.urls import resolve
from arkid.core.models import Tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        tenant = None
    
        # 通过tenant uuid正则获取request.tenant
        uuid4hex = re.compile('[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
        path = request.get_full_path()
        matchs = uuid4hex.findall(path)
        for match in matchs:
            tenant = Tenant.active_objects.filter(id=match).first()
            if tenant:
                break
        
        # 通过slug获取request.tenant
        # TODO
        # slug = get_slug()
        # if not tenant:
        #     tenant = Tenant.active_objects.filter(slug=slug).first()
        
        request.tenant = tenant
        request.operation_id = self.get_operation_id(request)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response

    def get_operation_id(self, request):
        view_func, _, _ = resolve(request.path)
        try:
            klass = view_func.__self__
            operation, _ = klass._find_operation(request)
            return operation.operation_id or klass.api.get_openapi_operation_id(operation)
        except:
            return ''