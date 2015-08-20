import sendgrid
from data import load_json
from . import sendgrid_conf

if not sendgrid_conf:
    sendgrid_conf = {
        'username': 'blah',
        'password': 'blah'
    }


_sclient = sendgrid.SendGridClient(username_or_apikey=sendgrid_conf['username'], password=sendgrid_conf['password'])

def send_mail(email_id, subject, body):
    email = sendgrid.Mail()
    email.add_to(email_id)
    email.set_subject(subject)
    email.set_html(body)
    email.set_from('<no-reply @ wadi.com>')
    return _sclient.send(email)
