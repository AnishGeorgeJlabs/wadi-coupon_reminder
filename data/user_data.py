from datetime import datetime
from data import execute_fn_dabba, execute_on_referaly

def get_user_data(coupons=None, days_past=None, today=None, debug=False):
    referally = get_user_data_from_referally(coupons, days_past, today, debug)
    footer = get_user_data_from_footer(coupons, days_past, today, debug)
    res = referally + footer
    for row in res:
        row[2] = row[2].replace('\n','').replace('\r','')
    return res

def get_user_data_from_footer(coupons=None, days_past=None, today=None, debug=False):
    return []

def get_user_data_from_referally(coupons=None, days_past=None, today=None, debug=False):
    if not today:
        today = datetime.now()
    td = today.strftime("%Y-%m-%d")

    # Language here is arabic/english
    base_query = """
    SELECT u.email, u.language, w.coupon
    FROM users u INNER JOIN wadi_v1_coupons w ON u.id=w.uid
    WHERE datediff('%s', date(u.time)) >= 7""" % td

    if coupons:
        base_query += " AND REPLACE(REPLACE(w.coupon, '\r', ''), '\n', '') IN ('%s')" % "','".join(coupons)
    if days_past:
        base_query += " AND date_add(date(u.time), interval 7 day) like '%s'" % td
    if debug:
        base_query += " limit 20"

    return execute_on_referaly(base_query)
