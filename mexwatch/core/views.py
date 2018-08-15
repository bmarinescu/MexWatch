import json
import logging

from django.http import Http404
from django.shortcuts import render, redirect

from core.models import User
from core.utils import SATOSHIS_PER_BTC, satoshis_to_btc, get_display_time, get_display_number, call_bitmex_api, \
    textToColor
from mexwatch.settings import JSON_INDENT

logger = logging.getLogger(__name__)


def frontpage(request):
    if User.objects.count() == 0:
        User.objects.create(name="benis", key_pub="4YFgfRe713-feq7ovWHtl_da",
                            key_secret="SWkuxaufF9G2n_YgLONCAKAvtPBwBBYy17ZW0Fn8kH2iUs0m")
    return redirect("user", User.objects.first().name)


def userpage(request, username):
    user_filter = User.objects.filter(name=username)
    if user_filter.count() == 0:
        raise Http404()

    user: User = user_filter.first()

    positions_json = call_bitmex_api('/position', api_key=user.key_pub, api_secret=user.key_secret)

    if 'error' in positions_json:
        user.delete()
        raise Http404()

    fills_json = call_bitmex_api('/execution/tradeHistory', {"reverse": "true"}, api_key=user.key_pub,
                                 api_secret=user.key_secret)
    order_json = call_bitmex_api('/order', {"reverse": "true", "filter": '{"ordStatus":"New", "ordType":"Limit"}'},
                                 api_key=user.key_pub, api_secret=user.key_secret)
    stop_json = call_bitmex_api('/order', {"reverse": "true", "filter": '{"ordStatus":"New", "ordType":"Stop"}'},
                                api_key=user.key_pub, api_secret=user.key_secret)
    instruments = call_bitmex_api('/instrument/indices', {"filter": '{"symbol":"."}'}, api_key=user.key_pub,
                                  api_secret=user.key_secret)
    wallet = call_bitmex_api('/user/wallet', api_key=user.key_pub, api_secret=user.key_secret)

    order_history = call_bitmex_api('/order', {"reverse": "true"}, api_key=user.key_pub, api_secret=user.key_secret)

    wallet_history = call_bitmex_api('/user/walletHistory', api_key=user.key_pub, api_secret=user.key_secret)

    wallet["amount"] = satoshis_to_btc(wallet["amount"])

    allUsers = User.objects.all()

    multiplier = 1
    if user.hide_balance and wallet["amount"] != 0:
        multiplier = 1 / wallet["amount"]

    wallet["amount"] *= multiplier

    for u in allUsers:
        w = call_bitmex_api('/user/wallet', api_key=u.key_pub, api_secret=u.key_secret)
        w["amount"] = satoshis_to_btc(w["amount"])

        u.multiplier = 1
        if u.hide_balance and w["amount"] != 0:
            u.multiplier = 1 / w["amount"]

        w["amount"] *= u.multiplier
        u.wallet = w

        pos = call_bitmex_api('/position', api_key=u.key_pub, api_secret=u.key_secret)
        total_pos_value = 0
        for p in pos:
            if p["symbol"] == "XBTUSD":
                p["value"] = abs(p["currentCost"]) / SATOSHIS_PER_BTC
            else:
                if p["markPrice"] is None: p["markPrice"] = 0
                p["value"] = float(p["currentQty"]) * float(p["markPrice"])
            total_pos_value += p["value"]
            p["value"] = get_display_number(p["value"])
        if w["amount"] != 0:
            if u.hide_balance:
                u.total_positions_value = get_display_number(multiplier * total_pos_value)
            else:
                u.total_positions_value = str(round(total_pos_value / w["amount"], 2)) + \
                                          "X ~ " + str(get_display_number(multiplier * total_pos_value))
        else:
            u.total_positions_value = 0
            w["amount"] = 0

    closed_positions_json = [item for item in positions_json if not item["isOpen"]]
    positions_json = [item for item in positions_json if item["isOpen"]]

    for cp in closed_positions_json:
        cp["prevRealisedPnl"] = str(satoshis_to_btc(cp["prevRealisedPnl"])) + " BTC"

    for p in positions_json:
        p['maintMargin'] = str(round(float(p["maintMargin"]) / SATOSHIS_PER_BTC, 2)) + \
                           (" (Cross)", "")[p["crossMargin"] == "1"]
        p["unrealisedGrossPnl"] = round(multiplier * p["unrealisedGrossPnl"] / SATOSHIS_PER_BTC, 4)
        p["realizedPnl"] = round(
            multiplier * (float(p["rebalancedPnl"]) + float(p["realisedPnl"])) / SATOSHIS_PER_BTC, 4)
        if p["symbol"] == "XBTUSD":
            p["value"] = p["currentCost"] / SATOSHIS_PER_BTC
        else:
            p["value"] = p["currentQty"] * p["markPrice"]
        p["value"] = abs(round(multiplier * p["value"], 4))
        p["timestamp"] = get_display_time(p["timestamp"])
        if p["currentQty"] < 0:
            p["side"] = "Short"
        else:
            p["side"] = "Long"

        p["currentQty"] = multiplier * p["currentQty"]

        p["currentQty"] = get_display_number(p["currentQty"])

    for s in stop_json:
        if not s["price"]:
            s["price"] = "Market"
        if not s["triggered"]:
            s["status"] = "Untriggered"
        s["timestamp"] = get_display_time(s["timestamp"])
        if not s["avgPx"]:
            s["avgPx"] = "-"

        s["cumQty"] = get_display_number(s["cumQty"] * multiplier)

    for h in order_history:
        if not h["price"]:
            h["price"] = "Market"
        h["timestamp"] = get_display_time(h["timestamp"])
        if h["ordType"] == "Stop":
            if not h["triggered"]:
                h["status"] = "Untriggered"
            else:
                h["status"] = "Triggered"
        else:
            h["status"] = "-"
            h["stopPx"] = "-"
        if h["side"] == "Sell":
            h["orderQty"] = "-" + str(h["orderQty"])

    for f in fills_json:
        f["shortId"] = f["orderID"][0:7]
        f["idColor"] = textToColor(f["orderID"])
        if f["symbol"][0:6] == "XBTUSD":
            f["value"] = str(f["orderQty"] / f["price"])[0:6]
        else:
            f["value"] = str(f["lastPx"] * f["orderQty"])[0:6]
        f["timestamp"] = get_display_time(f["timestamp"])

    for o in order_json:
        if o["symbol"][0:6] == "XBTUSD":
            o["value"] = str(multiplier * o["orderQty"] / o["price"])[0:6]
        else:
            o["value"] = str(multiplier * o["price"] * o["orderQty"])[0:6]
        o["timestamp"] = get_display_time(o["timestamp"])

        o["cumQty"] = get_display_number(o["cumQty"] * multiplier)
        o["orderQty"] = get_display_number(o["orderQty"] * multiplier)
        o["leavesQty"] = get_display_number(o["leavesQty"] * multiplier)

    return render(request, "core/index.html", {
        'currentUser': user,
        'fills': fills_json,
        'fillsDump': json.dumps(fills_json, indent=JSON_INDENT),
        'positions': positions_json,
        'positionsDump': json.dumps(positions_json, indent=JSON_INDENT),
        'closedPositions': closed_positions_json,
        'closedPositionsDump': json.dumps(closed_positions_json, indent=JSON_INDENT),
        'orders': order_json,
        'orderDump': json.dumps(order_json, indent=JSON_INDENT),
        'stops': stop_json,
        'stopsDump': json.dumps(stop_json, indent=JSON_INDENT),
        'users': allUsers,
        'instruments': json.dumps(instruments, indent=JSON_INDENT),
        'wallet': wallet,
        'walletDump': json.dumps(wallet),
        'history': order_history,
        'historyDump': json.dumps(order_history, indent=JSON_INDENT),
        'walletHistory': json.dumps(wallet_history, indent=JSON_INDENT),
    })
