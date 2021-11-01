from datetime import datetime
import json
from django import views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from app.models import App
from ..models import AppSubscribeRecord
from api.v1.serializers.app import AppListSerializer


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
@method_decorator(login_required, "dispatch")
class SubscribeAppList(views.View):

    def post(self, request, tenant_uuid):
        user = request.user
        data = []
        if hasattr(user, "app_subscribed_records"):
            apps = [record.app for record in user.app_subscribed_records.all()]
            data = AppListSerializer(apps, many=True).data

        return JsonResponse(
            data={
                "status": 200,
                "data": data
            }
        )
