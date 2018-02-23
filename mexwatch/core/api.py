from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.utils import json

from core.models import User
from core.utils import call_bitmex_api, get_http_response_for_key_error, get_error_http_response_object_not_found, \
    get_error_http_response

charts = ["balance", "profit"]


@csrf_exempt
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_charts(request):
    return HttpResponse(json.dumps({"charts": charts}, indent=2),
                        content_type="application/json")

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

    if chart_name == "balance":
        balance_history = call_bitmex_api('/user/walletHistory', api_key=user.key_pub, api_secret=user.key_secret)
        for b in balance_history:
            b["value"] = b["walletBalance"]


        res = {"chart_type": "line",
               "data": list(reversed(balance_history))}

        return HttpResponse(json.dumps(res, indent=2),
                            content_type="application/json", )
    elif chart_name == "profit":
        balance_history = call_bitmex_api('/user/walletHistory', api_key=user.key_pub, api_secret=user.key_secret)
        profit_history = []
        ignore_transactTypeList = ["Deposit","Withdrawal"]
        profit = 0
        profit_history.append({"timestamp": balance_history[-1]["timestamp"], "value": 0})
        for bh in reversed(balance_history):
            if bh["transactType"] not in ignore_transactTypeList:
                profit += bh["amount"]
                profit_history.append({"timestamp": bh["timestamp"], "value": profit})

        res = {"chart_type": "line",
               "data": profit_history}
        return HttpResponse(json.dumps(res, indent=2),
                            content_type="application/json", )
    else:
        return get_error_http_response_object_not_found("Chart", chart_name)
