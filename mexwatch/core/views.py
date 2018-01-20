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

from core.models import User

SATOSHIS_PER_BTC = 100000000


# noinspection PyDefaultArgument
def call_bitmex_api(url, get_params={}, api_key='4YFgfRe713-feq7ovWHtl_da',
                    api_secret=b'SWkuxaufF9G2n_YgLONCAKAvtPBwBBYy17ZW0Fn8kH2iUs0m'):
    api_url = 'https://www.bitmex.com'

    verb = 'GET'
    path = '/api/v1' + url
    expires = round(time.time() + 60)

    data_url = ""
    if len(get_params) > 0:
        data_url = "?" + urllib.parse.urlencode(get_params)

    signature = hmac.new(api_secret, str.encode(verb + path + data_url + str(expires)), hashlib.sha256).hexdigest()

    response = requests.get(api_url + path, get_params,
                            headers={'api-expires': str(expires),
                                     'api-key': api_key,
                                     'api-signature': signature})
    return response


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
    fills = call_bitmex_api('/execution/tradeHistory', {"reverse": "true"})
    fills_json = json.loads(fills.text)

    positions = call_bitmex_api('/position')
    positions_json = json.loads(positions.text)

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
                                               'positionsDump': json.dumps(positions_json, indent=2), })


def create_user(request):
    if request.method != "POST":
        raise Http404

    try:
        name = request.POST["key_name"]
        key_pub = request.POST["key_pub"]
        key_secret = request.POST["key_secret"]
    except KeyError as e:
        return get_http_response_for_key_error(e)

    response = {}

    if User.objects.filter(name=name).count() != 0:
        return get_err_response(409, "Name already taken.")

    apiKeyJson = call_bitmex_api('/apiKey', api_key=key_pub, api_secret=key_secret)

    if apiKeyJson["error"]:
        return get_err_response(400, "Invalid API key/secret pair")
    elif len(apiKeyJson["permissions"]) != 0:
        return get_err_response(400, "Please add a key that has no permissions assigned to it")
    else:
        User.objects.create(name=name, key_pub=key_pub, key_secret=key_secret)

    return HttpResponse(
        "{}",
        content_type="application/json",
        status=200
    )
