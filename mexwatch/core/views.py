import hashlib
import hmac
import json
import logging
import time
import types
import urllib.parse
from pprint import pprint

from django.contrib.sites import requests
from django.http import Http404, HttpResponse
from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt

from core.models import User

SATOSHIS_PER_BTC = 100000000


# noinspection PyDefaultArgument
def call_bitmex_api(url, get_params={}, api_key='4YFgfRe713-feq7ovWHtl_da',
                    api_secret='SWkuxaufF9G2n_YgLONCAKAvtPBwBBYy17ZW0Fn8kH2iUs0m'):
    api_url = 'https://www.bitmex.com'

    b = bytearray()
    b.extend(map(ord, api_secret))
    api_secret = b

    verb = 'GET'
    path = '/api/v1' + url
    expires = round(time.time() + 60)

    data_url = ""
    if len(get_params) > 0:
        data_url = "?" + urllib.parse.urlencode(get_params)

    signature = hmac.new(b, str.encode(verb + path + data_url + str(expires)), hashlib.sha256).hexdigest()

    response = requests.get(api_url + path, get_params,
                            headers={'api-expires': str(expires),
                                     'api-key': api_key,
                                     'api-signature': signature})
    return json.loads(response.text)


logger = logging.getLogger(__name__)


def get_http_response_for_key_error(e: KeyError, message=""):
    logger.exception("")
    return HttpResponse(e.__str__, status=400)


def get_err_response(status, message):
    return HttpResponse(
        json.dumps({"err": message}),
        content_type="application/json",
        status=status
    )


# Create your views here.
def frontpage(request):
    fills_json = call_bitmex_api('/execution/tradeHistory', {"reverse": "true"})

    positions_json = call_bitmex_api('/position')

    for p in positions_json:
        if p["isOpen"]:
            p['maintMargin'] = str(round(float(p["maintMargin"]) / SATOSHIS_PER_BTC, 2)) + \
                               (" (Cross)", "")[p["crossMargin"] == "1"]
            p["unrealisedGrossPnl"] = round(p["unrealisedGrossPnl"] / SATOSHIS_PER_BTC, 4)
            p["realizedPnl"] = round((float(p["rebalancedPnl"]) + float(p["realisedPnl"])) / SATOSHIS_PER_BTC, 4)
            p["value"] = p["currentQty"] * p["markPrice"]

    return render(request, "core/index.html", {'fills': fills_json,
                                               'fillsDump': json.dumps(fills_json, indent=2),
                                               'positions': positions_json,
                                               'positionsDump': json.dumps(positions_json, indent=2),
                                               'users': User.objects.all()})

@csrf_exempt
def create_user(request):
    if request.method != "POST":
        raise Http404

    try:
        name = request.POST["key_name"]
        key_pub = request.POST["key_pub"]
        key_secret = request.POST["key_secret"]
    except KeyError as e:
        return get_http_response_for_key_error(e)

    if User.objects.filter(name=name).count() != 0:
        return get_err_response(409, "Name already taken.")

    api_key_json = call_bitmex_api('/apiKey', api_key=key_pub, api_secret=key_secret)
    if "error" in api_key_json and api_key_json["error"]["name"] == "HTTPError":
        return get_err_response(400, "Invalid API key/secret pair")

    api_key_json = api_key_json[0]
    if len(api_key_json["permissions"]) != 0:
        return get_err_response(400, "Please add a key that has no permissions assigned to it")

    existing_user_query = User.objects.filter(key_pub=key_pub, key_secret=key_secret)
    if existing_user_query.count() == 0:
        User.objects.create(name=name, key_pub=key_pub, key_secret=key_secret)

        return HttpResponse(
            '{"message" : "User created!"}',
            content_type="application/json",
            status=200
        )
    else:
        assert existing_user_query.count() == 1
        existing_user : User = existing_user_query.first()
        existing_user.name = name
        existing_user.save()


        return HttpResponse(
            '{"message" : "Display name has been replaced"}',
            content_type="application/json",
            status=200
        )
