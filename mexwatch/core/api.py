from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.utils import json

from core.models import User
from core.utils import call_bitmex_api, get_http_response_for_key_error, get_error_http_response_object_not_found, \
    get_error_http_response

charts = ["balanceHistory"]

@csrf_exempt
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_charts(request):
    return HttpResponse(str(charts))

@csrf_exempt
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_chart_data(request):
    try:
        username = request.GET["username"]
        chart_name = request.GET["chart_name"]
    except KeyError as e:
        return get_http_response_for_key_error(e)

    user_filter = User.objects.filter(name=username)
    if user_filter.count() == 1:
        user = user_filter.first()
    elif user_filter.count() == 0:
        return get_error_http_response_object_not_found("User", username)
    else:
        assert False, "Multiple users with the same username in database" #should not happen

    if chart_name == "balanceHistory":
        wallet_history = call_bitmex_api('/user/walletHistory', api_key=user.key_pub, api_secret=user.key_secret)
        res = {"chart_type":"line",
               "data": wallet_history}
        return HttpResponse(json.dumps(res, indent=2))
    else:
        return get_error_http_response_object_not_found("Chart", chart_name)

