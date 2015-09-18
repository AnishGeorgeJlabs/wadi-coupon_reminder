import httplib2
# Do OAuth2 stuff to create credentials object
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client import tools
import gspread
import os


def _local_file(name):
    cdir = os.path.dirname(__file__)
    filename = os.path.join(cdir, name)
    return filename

def _get_worksheet():
    storage = Storage(_local_file("creds.data"))
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flags = tools.argparser.parse_args(args=[])
        flow = flow_from_clientsecrets(_local_file("client_secret.json"),
                                       scope=["https://spreadsheets.google.com/feeds"])
        credentials = tools.run_flow(flow, storage, flags)
    if credentials.access_token_expired:
        credentials.refresh(httplib2.Http())

    gc = gspread.authorize(credentials)

    return gc.open_by_key('144fuYSOgi8md4n2Ezoj9yNMi6AigoXrkHA9rWIF0EDw')

def get_reminder_sheet():
    return _get_worksheet().get_worksheet(1)
