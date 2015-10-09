"""
Main Module for the coupon reminder system
"""

from datetime import datetime
import logging

from jinja2 import Environment, PackageLoader
from data.email import send_mail
from data.external.sheet import get_days_from_sheet

logging.basicConfig(filename='./log', level=logging.DEBUG)

env = Environment(loader=PackageLoader('data', 'templates'))
template_en = env.get_template('email_en.html')
template_ar = env.get_template('email_ar.html')

# Some external code from stack overflow
def ord(n):
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def dtStylish(dt, f):
    return dt.strftime(f).replace("{th}", ord(dt.day))


# --------------------------------------



def run(data, subject="Coupon Reminder (Wadi)"):
    success = 0
    failure = 0
    for user_data in data:
        dt = dtStylish(user_data['date'], "{th} %B, %Y")
        if user_data['language'] == 'english':
            template = template_en
        else:
            template = template_ar
        content = template.render(coupons=user_data['coupons'], target=dt)
        res = send_mail(email_id=user_data['email'], subject=subject, body=content)
        if int(res[0]) == 200:
            success += 1
        else:
            failure += 1
    logging.info("Report - %s - Success: %i, Failure: %i" % (datetime.now().strftime("%d/%m/%Y"), success, failure))


def test():
    data = [
        {
            'email': 'anish.george@jlabs.co',
            'language': 'arabic',
            'coupons': [
                {
                    'code': 'WELCOMEwadi',
                    'amount': '100 AED',
                    'total': '500 AED'
                }
            ],
            'date': datetime.now()
        }
    ]
    run(data, "Test1 coupon reminder")


def beta_test():
    from data.coupon_load import get_data

    init_data = get_data(True)
    if len(init_data.keys()) == 0:
        print "Zero data for debugging"
    else:
        init_data[0]['email'] = 'anish.george@jlabs.co'
        run(init_data[:1], "Beta testing, coupon reminder")


def final_test(emails, language=None):
    from data.coupon_load import get_data

    init_data = get_data(debug=True, days_left=5)
    n = len(emails) if len(emails) <= len(init_data) else len(init_data)
    if n == 0:
        print "No data !!!!"
        return False

    final_data = []
    for i in range(n):
        init_data[i]['email'] = emails[i]
        if language:
            init_data[i]['language'] = language
        final_data.append(init_data[i])

    if n < len(emails):
        for email in emails[n:]:
            d = init_data[0].copy()
            d['email'] = email
            if language:
                d['language'] = language
            final_data.append(d)

    run(final_data, "Coupon reminder final test")
    return True


if __name__ == '__main__':
    from data.coupon_load import get_data
    from data.block.blocking import block_filter

    config = get_days_from_sheet()
    for dc in config:
        data = get_data(days_left=dc[0], days_past=dc[1])
        run(block_filter(data))
