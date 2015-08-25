from data import execute_fn_dabba, execute_on_referaly
import requests
from datetime import datetime, timedelta
import json
from phpserialize import unserialize


def get_data(debug=False):
    """
    Master function, get a dictionary of emails against codes data
    :param debug: if True, will always give value
    :return:
    >> columns: email | code | currency | discount type | amount | percentage | conditions (serialized)
    """
    codes, data = get_codes(get_days(), debug)

    c_list = "','".join(codes)

    query = """SELECT users.email, wadi_v1_coupons.coupon
    FROM users, wadi_v1_coupons where users.id=wadi_v1_coupons.uid AND
    REPLACE(REPLACE(wadi_v1_coupons.coupon, '\r', ''), '\n', '')
    IN ('%s') order by users.id""" % (c_list)

    '''
    Columns:
    email | coupon
    '''

    if debug is True:
        query += " limit 10"

    rdata = execute_on_referaly(query)
    for record in rdata:
        record += data[record[1]]

    rdata = filter(lambda k: len(k) > 0,
                   map(_transform, rdata))

    return _convert_data(rdata)


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

def get_target_date():
    """ Simple function to get the target expiry date """
    return datetime.now() + timedelta(days=get_days())

def get_codes(days, debug=False):
    """
    Get the codes data from bob_live_sa and ae

    :param days: # of days for the coupon to expire
    :param debug: if True, will always return some value as the date will be fixed
    :return: (list, dict)
    >> columns:  code | currency | discount type | amount | percentage | conditions (serialized)
    """
    if not debug:
        max_date = get_target_date().strftime('%Y-%m-%d')
    else:
        max_date = '2015-05-31'

    query = """
    SELECT sr.code, sr.discount_amount_currency,
           srs.discount_type, srs.discount_amount_default, srs.discount_percentage, srs.conditions_ruleset
    FROM sales_rule sr INNER JOIN sales_rule_set srs ON sr.fk_sales_rule_set = srs.id_sales_rule_set
    WHERE sr.is_active = 1 AND DATE(sr.to_date) LIKE '%s'
    """ % max_date

    table = execute_fn_dabba("bob_live_sa")(query)
    table += execute_fn_dabba("bob_live_ae")(query)

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


def _transform(record):
    """
    Converts the record into a 2 sized list of email id and coupon data
    :param record:
    :return:
    """
    res = [record[0]]   # [email]
    cdata = record[1:]  # [ 0:code, 1:currency, 2:discount type, 3:amount, 4:percentage, 5:conditions

    currency = cdata[1]
    try:
        coupon_condition = unserialize(cdata[5])
        subtotal = _sanitize(coupon_condition['Subtotal']) + " " + currency
    except:
        return []

    discount_type = cdata[2]

    if discount_type == 'fixed':
        amt = str(cdata[3]) + " " + str(currency)
    else:
        amt = _sanitize(cdata[4]) + "%"

    res.append({
        'code': cdata[0],
        'amount': amt,
        'total': subtotal
    })

    return res


def _convert_data(records):
    """
    converts the given table into dictionary of user emails against code data
    :param records: A List of lists, each sublist must be 2 items in length, the email id and the coupon data
    :return:
    """

    res = {}
    for record in records:
        email = record[0]
        if email in res:
            res[email].append(record[1])
        else:
            res[email] = [record[1]]
    return res
