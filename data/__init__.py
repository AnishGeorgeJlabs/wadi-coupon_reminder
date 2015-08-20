__author__ = 'jlabs-11'

import os
import json

def load_json(file):
    """ Load json from a configuration file
    :param file: The filename, relative path from this directory
    :rtype: dict
    """
    cdir = os.path.dirname(__file__)
    filename = os.path.join(cdir, file)
    try:
        with open(filename, 'r') as cfile:
            return json.loads(cfile.read())
    except Exception:
        return {}

sql_conf = load_json('sql_conf.json')
sendgrid_conf = load_json('sendgrid_conf.json')
