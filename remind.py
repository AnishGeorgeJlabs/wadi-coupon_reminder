"""
Main Module for the coupon reminder system
"""

from jinja2 import Environment, PackageLoader
from data.email import send_mail
from datetime import datetime, timedelta
import logging

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



def run(data, target_date, subject="Coupon Reminder (Wadi)"):
    dt = dtStylish(target_date, "{th} %B, %Y")
    success = 0
    failure = 0
    for email_id, user_data in data.items():
        if user_data['language'] == 'english':
            template = template_en
        else:
            template = template_ar
        content = template.render(coupons=user_data['coupons'], target=dt)
        res = send_mail(email_id=email_id, subject=subject, body=content)
        if int(res[0]) == 200:
            success += 1
        else:
            failure += 1
    '''
    for email_id, coupons in data.items():
        content = template.render(coupons=coupons, target=dt)
        res = send_mail(email_id=email_id, subject=subject, body=content)
        if int(res[0]) == 200:
            success += 1
        else:
            failure += 1
    '''
    logging.info("Report - %s - Success: %i, Failure: %i" % (datetime.now().strftime("%d/%m/%Y"), success, failure))



def test():
    data = {
        'anish.george@jlabs.co': {
            'language': 'english',
            'coupons': [
                {
                    'code': 'WELCOMEwadi',
                    'amount': '400 AED',
                    'total': '100 AED'
                }
            ]
        }
    }
    run(data, datetime.now() + timedelta(days=7), "Test1 coupon reminder")


def beta_test():
    from data.coupon_load import get_data
    init_data, d = get_data(True)
    if len(init_data.keys()) == 0:
        print "Zero data for debugging"
    else:
        final_data = {
            'anish.george@jlabs.co': init_data[init_data.keys()[0]]
        }
        run(final_data, datetime.now() + timedelta(days=20), "Beta testing, coupon reminder")


def final_test(emails):
    from data.coupon_load import get_data
    init_data, d = get_data(True)
    n = len(emails) if len(emails) <= len(init_data) else len(init_data)
    if n == 0:
        print "No data !!!!"
        return False

    final_data = {}
    for i in range(n):
        final_data[emails[i]] = init_data[i]

    if n < len(emails):
        for email in emails[n:]:
            final_data[email] = init_data[0]
    run(final_data, d, "Coupon reminder final test")
    return True



if __name__ == '__main__':
    from data.coupon_load import get_data
    data, tm = get_data()
    run(data, tm)
