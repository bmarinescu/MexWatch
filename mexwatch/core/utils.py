import hashlib
import hmac
import json
import time
import urllib.parse
import zlib

import requests
from django.http import HttpResponse

SATOSHIS_PER_BTC = 100000000


def satoshis_to_btc(satoshis):
    if satoshis == 0:
        return 0
    return round(satoshis / SATOSHIS_PER_BTC, 4)


def get_display_time(time_str):
    return time_str[0:19].replace("T", " ") + " UTC"


def get_display_number(x):
    is_negative = x < 0
    e = '%.4e' % x
    if is_negative:
        ms = e[1] + e[3:6]  # most significant digits
        exp = int(e[8:])
    else:
        ms = e[0] + e[2:5]  # most significant digits
        exp = int(e[7:])

    neg = "-" if is_negative else ""
    if exp <= -4:
        return e
    elif exp <= 2:
        return round(x, 3 - exp)
    elif exp <= 4:
        return int(x)
    elif exp == 5:
        return neg + ms[0:3] + "." + ms[3] + "k"
    elif exp == 6:
        return neg + ms[0] + "." + ms[1:4] + "m"
    elif exp == 7:
        return neg + ms[0:2] + "." + ms[2:4] + "m"
    elif exp == 8:
        return neg + ms[0:3] + "." + ms[3] + "m"
    elif exp == 9:
        return neg + ms[0] + "." + ms[1:4] + "b"
    else:
        return e


# noinspection PyDefaultArgument
def call_bitmex_api(url, get_params={}, api_key='4YFgfRe713-feq7ovWHtl_da',
                    api_secret='SWkuxaufF9G2n_YgLONCAKAvtPBwBBYy17ZW0Fn8kH2iUs0m'):
    api_url = 'https://www.bitmex.com'

    secret_bytes = str_to_bytes(api_secret)

    verb = 'GET'
    path = '/api/v1' + url
    expires = round(time.time() + 60)

    data_url = ""
    if len(get_params) > 0:
        data_url = "?" + urllib.parse.urlencode(get_params)

    signature = hmac.new(secret_bytes, str.encode(verb + path + data_url + str(expires)), hashlib.sha256).hexdigest()

    response = requests.get(api_url + path, get_params,
                            headers={'api-expires': str(expires),
                                     'api-key': api_key,
                                     'api-signature': signature})
    # print("API CALL: " + url + " key:" + api_key[0:4] + " remaining: " + response.headers[
    #     "x-ratelimit-remaining"] + " / time-remaining: "
    #       + response.headers["x-ratelimit-reset"])
    return json.loads(response.text)


def str_to_bytes(str):
    b = bytearray()
    b.extend(map(ord, str))
    return b


def get_http_response_for_key_error(e: KeyError, message=""):
    return HttpResponse(e.__str__, status=400)


def get_error_http_response(status: int, message: str):
    return HttpResponse(
        json.dumps({"err": message}),
        content_type="application/json",
        status=status
    )


def get_error_http_response_object_not_found(objType: str, id="?"):
    return get_error_http_response(412, "Could not find " + objType + ": '" + str(id) + "'")


def textToColor(text):
    code = hex(zlib.crc32(str_to_bytes(text)))
    code = code[2:8]
    return code
