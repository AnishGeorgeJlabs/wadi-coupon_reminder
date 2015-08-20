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
        max_date = '2015-05-31'

    query = """
    SELECT code FROM sales_rule
    WHERE is_active = 1 AND date(to_date) LIKE '%s'""" % max_date

    table = execute_fn_dabba("bob_live_sa")(query)
    table += execute_fn_dabba("bob_live_ae")(query)

    return map(lambda k: k[0], table)

def get_data(debug=False):
    codes = get_codes(get_days(), debug)

    c_list = "','".join(codes)
    '''
    query = """SELECT users.time,users.email,wadi_v1_coupons.coupon,wadi_v1_coupons.type
    FROM users,wadi_v1_coupons where users.id=wadi_v1_coupons.uid AND
    SUBSTRING(wadi_v1_coupons.coupon, 1, CHAR_LENGTH(wadi_v1_coupons.coupon) - 2)
    IN ('%s') order by users.id""" % (c_list)
    '''

    query = """SELECT users.time,users.email,wadi_v1_coupons.coupon,wadi_v1_coupons.type
    FROM users,wadi_v1_coupons where users.id=wadi_v1_coupons.uid AND
    REPLACE(REPLACE(wadi_v1_coupons.coupon, '\r', ''), '\n', '')
    IN ('%s') order by users.id""" % (c_list)


    if debug is True:
        query += " limit 10"

    return execute_on_referaly(query)
