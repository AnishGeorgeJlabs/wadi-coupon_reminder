from datetime import datetime, timedelta

import requests

from data import execute_fn_dabba
from phpserialize import unserialize
from user_data import get_user_data


def get_data(debug=False, days_past=None, days_left=None, today=None):
    if not days_past and not days_left:
        return {}, None

    codes, cdata = get_codes(days_left=days_left, debug=debug, today=today)
    users = get_user_data(coupons=codes, days_past=days_past, today=today)

    for record in users:
        record += cdata[record[2]]

    final_users = filter(lambda k: len(k) > 0,
                         map(_transform, users))
    return _convert_data(final_users)


def get_days():
    """ Get the number of days configuration from external server """
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


def get_target_date(days):
    """ Simple function to get the target expiry date """
    return datetime.now() + timedelta(days=days)


def get_codes(days_left=None, debug=False, today=None):
    """
    :param days_left: The expiry date of the coupon, if not present, returns all coupons who have a week or more to expire,
                      which will be used in the case of one week after signup situation
    :param debug:
    :param today:
    :return:
    """
    if not today:
        today = datetime.now()
    td = today.strftime("%Y-%m-%d")

    base_query = """
    SELECT sr.code, sr.discount_amount_currency,
           srs.discount_type, srs.discount_amount_default, srs.discount_percentage, srs.conditions_ruleset, sr.to_date
    FROM sales_rule sr INNER JOIN sales_rule_set srs ON sr.fk_sales_rule_set = srs.id_sales_rule_set
    WHERE sr.is_active = 1 AND datediff(DATE(sr.to_date), '%s') >= 7
    """ % td

    if days_left:
        if not debug:
            max_date = get_target_date(days_left).strftime('%Y-%m-%d')
        else:
            max_date = '2015-05-31'
        base_query += " AND DATE(sr.to_date) LIKE '%s'" % max_date

    table = execute_fn_dabba("bob_live_sa")(base_query)
    table += execute_fn_dabba("bob_live_ae")(base_query)

    codes = map(lambda k: k[0], table)
    coupon_dict = {}
    for row in table:
        coupon_dict[row[0]] = row[1:]

    return codes, coupon_dict


def _sanitize(amount):
    """ Simple function to turn a string like '100.00' into '100' """
    amount = str(amount)
    if '.00' in amount:
        return amount.split('.')[0]
    else:
        return amount


def _transform(record):
    """
    Converts the record into a 2 sized list of email id, language and coupon data
    :param record:
    :return:
    """
    res = record[:2]  # [email, language]
    cdata = record[2:]  # [ 0:code, 1:currency, 2:discount type, 3:amount, 4:percentage, 5:conditions, 6: date

    currency = cdata[1]
    try:
        coupon_condition = unserialize(cdata[5])
        subtotal = _sanitize(coupon_condition['Subtotal']) + " " + str(currency)
    except:
        print "Transformation, dropping 1"
        return []

    discount_type = cdata[2]

    if discount_type == 'fixed':
        amt = _sanitize(cdata[3]) + " " + str(currency)
    else:
        amt = _sanitize(cdata[4]) + "%"

    res.append({
        'code': cdata[0],
        'amount': amt,
        'total': subtotal,
        'date': cdata[6]
    })
    return res


def _convert_data(records):
    """
    TODO
    converts the given table into dictionary of user emails against code data
    and then returns as a list of entries, not a dictionary
    :return:
    """

    res = {}
    for record in records:
        email = record[0]
        date = record[2].pop('date')
        if email in res:
            res[email]['coupons'].append(record[2])
            if res[email]['date'] > date:
                res[email]['date'] = date
        else:
            res[email] = {
                'language': record[1],
                'coupons': [record[2]],
                'date': date
            }

    final = []
    for key, value in res.items():
        value['email'] = key
        final.append(value)
    return final
