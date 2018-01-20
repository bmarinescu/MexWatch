import hashlib
import hmac
import json
import logging
import time
import types
import urllib.parse
from pprint import pprint

from django.contrib.sites import requests
from django.shortcuts import render
import requests

SATOSHIS_PER_BTC = 100000000


# noinspection PyDefaultArgument
def call_bitmex_api(url, get_params={}):
    api_key = '4YFgfRe713-feq7ovWHtl_da'
    api_secret = b'SWkuxaufF9G2n_YgLONCAKAvtPBwBBYy17ZW0Fn8kH2iUs0m'
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


# Create your views here.
def frontpage(request):
    fills = call_bitmex_api('/execution/tradeHistory', {"reverse": "true"})
    fills_json = json.loads(fills.text)

    positions = call_bitmex_api('/position')
    positions_json = json.loads(positions.text)

    for p in positions_json:
        p['maintMargin'] = str(round(float(p["maintMargin"]) / SATOSHIS_PER_BTC, 2)) + \
                                  (" (Cross)", "")[p["crossMargin"] == "1"]
        p["unrealisedGrossPnl"] = round(p["unrealisedGrossPnl"]/SATOSHIS_PER_BTC, 4)
        p["realizedPnl"] = round((float(p["rebalancedPnl"]) + float(p["realisedPnl"])) / SATOSHIS_PER_BTC, 4)

    return render(request, "core/index.html", {'fills': fills_json,
                                               'fillsDump': json.dumps(fills_json, indent=2),
                                               'positions': positions_json,
                                               'positionsDump': json.dumps(positions_json, indent=2), })
