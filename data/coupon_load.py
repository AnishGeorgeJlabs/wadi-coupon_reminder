from data import execute_fn_dabba, execute_on_referaly
import requests
from datetime import datetime, timedelta
import json

def get_days():
    default = 5
    url = "http://45.55.72.208/wadi/configuration/coupon_reminder/days_limit"
    response = requests.get(url)
    if response.status_code != 200:
        return default
    else:
        data = response.json()
        if not data['success']:
            return default
        else:
            return int(data['value'])

def get_codes(days, debug=False):
    if not debug:
        max_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    else:
        max_date = '2015-07-31'

    query = """
    SELECT code FROM sales_rule
    WHERE is_active = 1 AND date(to_date) LIKE '%s'""" % max_date

    table = execute_fn_dabba("bob_live_sa")(query)
    table += execute_fn_dabba("bob_live_ae")(query)

    return map(lambda k: k[0], table)

def get_data(debug=False):
    codes = get_codes(get_days(), debug)

    query = """
    SELECT users.time, users.email, w.coupons, w.type
    FROM users JOIN wadi_v1_coupons w on users.id=w.uid
    WHERE SUBSTRING(w.coupon, 1, CHAR_LENGTH(w.coupon) - 2) IN (%s) """ % json.dumps(codes).strip("[]")

    if debug is True:
        query += " limit 10"

    return execute_on_referaly(query)
