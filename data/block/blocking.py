import os
import json

'''
def _local_file(name):
    cdir = os.path.dirname(__file__)
    filename = os.path.join(cdir, name)
    return filename
'''

record_file = os.path.join(os.path.dirname(__file__), 'today_emails.json')

def block_filter(data):
    try:
        with open(record_file, 'r') as e_file:
            existing = json.load(e_file)
    except IOError:
        existing = []

    new_data = filter(
        lambda d: d['email'] not in existing,
        data
    )

    new_emails = [x['email'] for x in new_data]
    with open(record_file, 'w') as e_file:
        json.dump(existing + new_emails, e_file)

    return new_data
