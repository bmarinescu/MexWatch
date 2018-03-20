from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.utils import json

from core.models import User
from core.utils import call_bitmex_api, get_error_http_response_object_not_found, get_http_response_for_key_error, \
    get_error_http_response
from mexwatch.settings import JSON_INDENT

charts = ["balance", "profit"]


@csrf_exempt
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_charts(request):
    return HttpResponse(json.dumps({"charts": charts}, indent=JSON_INDENT),
                        content_type="application/json")

@csrf_exempt
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_chart_data(request):
    username = request.GET.get("username")
    chart_name = request.GET.get("chart_name")

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

        return HttpResponse(json.dumps(res, indent=JSON_INDENT),
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
        return HttpResponse(json.dumps(res, indent=JSON_INDENT),
                            content_type="application/json", )
    else:
        return get_error_http_response_object_not_found("Chart", chart_name)


@csrf_exempt
@api_view(['POST'])
def create_user(request):
    try:
        name = request.POST["key_name"]
        key_pub = request.POST["key_pub"]
        key_secret = request.POST["key_secret"]
    except KeyError as e:
        return get_http_response_for_key_error(e)

    hide_balances = request.POST.get("hide_balance", "false")

    if User.objects.filter(name=name).count() != 0:
        return get_error_http_response(409, "Name already taken.")

    api_key_json = call_bitmex_api('/apiKey', api_key=key_pub, api_secret=key_secret)
    if "error" in api_key_json and api_key_json["error"]["name"] == "HTTPError":
        return get_error_http_response(400, "Invalid API key/secret pair")

    api_key_json = api_key_json[0]
    if len(api_key_json["permissions"]) != 0:
        return get_error_http_response(400, "Please add a key that has no permissions assigned to it")

    existing_user_query = User.objects.filter(key_pub=key_pub, key_secret=key_secret)
    if existing_user_query.count() == 0:
        User.objects.create(name=name, key_pub=key_pub, key_secret=key_secret, hide_balance=(hide_balances == "on"))

        return HttpResponse(
            '{"message" : "User created!"}',
            content_type="application/json",
            status=200
        )
    else:
        assert existing_user_query.count() == 1
        existing_user: User = existing_user_query.first()
        existing_user.name = name
        existing_user.hide_balance = (hide_balances == "on")
        existing_user.save()

        return HttpResponse(
            '{"message" : "Display name has been replaced"}',
            content_type="application/json",
            status=200
        )

