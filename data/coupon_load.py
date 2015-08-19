from data import execute_fn_dabba, execute_fn_referaly
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

def get_codes(days):
    max_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    query = """
    SELECT code FROM sales_rule
    WHERE is_active = 1 AND date(to_date) LIKE '%s'""" % max_date

    table = execute_fn_dabba("bob_live_sa")(query)
    table += execute_fn_dabba("bob_live_ae")(query)

    return map(lambda k: k[0], table)
