"""
Main Module for the coupon reminder system
"""

from jinja2 import Environment, PackageLoader
from data.email import send_mail
from datetime import datetime, timedelta

env = Environment(loader=PackageLoader('data', 'templates'))
template = env.get_template('email.html')

# Some external code from stack overflow
def ord(n):
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

def dtStylish(dt, f):
    return dt.strftime(f).replace("{th}", ord(dt.day))
# --------------------------------------



def run(data, target_date):
    dt = dtStylish(target_date, "{th} %B, %Y")
    for email_id, coupons in data.items():
        content = template.render(coupons=coupons, target=dt)
        send_mail(email_id=email_id, subject="Voucher reminder from Wadi", body=content)


def test():
    data = {
        'anish.george@jlabs.co': [
            {
                'code': 'WELCOMEwadi',
                'amount': '400 AED',
                'total': '100 AED'
            }
        ]
    }
    run(data, datetime.now() + timedelta(days=7))


def beta_test():
    from data.coupon_load import get_data
    init_data, d = get_data(True)
    final_data = {
        'anish.george@jlabs.co': init_data[init_data.keys()[0]]
    }
    run(final_data, datetime.now() + timedelta(days=20))


if __name__ == '__main__':
    pass
