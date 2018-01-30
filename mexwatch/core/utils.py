SATOSHIS_PER_BTC = 100000000


def satoshis_to_btc(satoshis):
    if satoshis == 0:
        return 0
    return round(satoshis / SATOSHIS_PER_BTC, 4)


def get_display_time(time_str):
    return time_str[0:19].replace("T", " ") + " UTC"


def specialRound(p):
    if p == 0:
        return 0
    if abs(p) >= 100:
        p = int(p)
    else:
        p = round(p, 4)
    return p