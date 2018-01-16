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

# noinspection PyDefaultArgument
SATOSHIS_PER_BTC = 100000000


def call_bitmex_api(url, get_params={}):
    apiKey = '4YFgfRe713-feq7ovWHtl_da'
    apiSecret = b'SWkuxaufF9G2n_YgLONCAKAvtPBwBBYy17ZW0Fn8kH2iUs0m'
    apiUrl = 'https://www.bitmex.com'

    verb = 'GET'
    path = '/api/v1' + url
    expires = round(time.time() + 60)

    data_url = ""
    if len(get_params) > 0:
        data_url = "?" + urllib.parse.urlencode(get_params)

    signature = hmac.new(apiSecret, str.encode(verb + path + data_url + str(expires)), hashlib.sha256).hexdigest()

    # print("signature= " + signature)
    # print("data_url= " + data_url)
    # print("timetime= " + str(time.time()))
    # print("timeround= " + str(round(time.time())))
    # print("expires= " + str(expires))
    # print("apiUrl + path= " + apiUrl + path)
    #
    # logging.basicConfig(level=logging.DEBUG)

    response = requests.get(apiUrl + path, get_params,
                            headers={'api-expires': str(expires),
                                     'api-key': apiKey,
                                     'api-signature': signature})
    # print("headers = " + str(response.request.headers))
    return response


# Create your views here.
def frontpage(request):
    fills = call_bitmex_api('/execution/tradeHistory', {"reverse": "true"})
    fills_json = json.loads(fills.text)

    positions = call_bitmex_api('/position')
    positions_json = json.loads(positions.text)
    # round($position["maintMargin"]/$satoshis_per_btc, 2) . ($position["crossMargin"] == "1" ? " (Cross)" : "");
    for position in positions_json:
        position['maintMargin'] = str(round(float(position["maintMargin"]) / SATOSHIS_PER_BTC, 2)) + \
                                  (" (Cross)", "")[position["crossMargin"] == "1"]
        position["unrealisedGrossPnl"] = round(position["unrealisedGrossPnl"]/SATOSHIS_PER_BTC, 4)
        position["realizedPnl"] = round((float(position["rebalancedPnl"]) + float(position["realisedPnl"])) / SATOSHIS_PER_BTC, 4)

    return render(request, "core/index.html", {'fills': fills_json,
                                               'fillsDump': json.dumps(fills_json, indent=2),
                                               'positions': positions_json,
                                               'positionsDump': json.dumps(positions_json, indent=2), })
