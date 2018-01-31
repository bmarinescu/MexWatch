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
