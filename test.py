import pyspread

import httplib2
import os

import sys

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = "PySpread"

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'script-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

print("starting...")
sys.stdout.flush()
credentials = get_credentials()
print("Got credentials")
sys.stdout.flush()
user = pyspread.authorize(credentials)
print("Got user")
sys.stdout.flush()
ss = user.open_by_url('https://docs.google.com/spreadsheets/d/1LIDeC3yZCF43D4z3EPusOwOxqjpAFBcoRfF8csnySPk/edit')
print("Got ss")
sys.stdout.flush()
sheet = ss.get_sheet("Draft1")
print("Got sheet")
sys.stdout.flush()
#get_column(self, c, r_offset, n_rows)
result = sheet.get_column(1,2,10)
print(result)