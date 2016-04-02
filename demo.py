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

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
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
    credentials.refresh(httplib2.Http()) # prevents the credentials from timing out
    return credentials

print("Starting...")
sys.stdout.flush()
credentials = get_credentials()
print("Connecting to spreadsheet...")
sys.stdout.flush()
user = pyspread.authorize(credentials)
ss = user.open_by_url('https://docs.google.com/spreadsheets/d/1VB8V2MdhyBQdvxMxssjGkk_8Yq9OY60VtNiOfTJXJsc/edit')
sheet = ss.get_sheet("Sheet1")
print("Find B2")
sys.stdout.flush()
raw_input() # pauses the program until you hit enter
print(sheet.get_cell_value(2, 2))
sys.stdout.flush()
raw_input()
print("Find range from (1, 1) to (3, 3)")
sys.stdout.flush()
raw_input()
print(sheet.get_range_values(1, 1, 3, 3))
sys.stdout.flush()
raw_input()
print("Find row 1")
sys.stdout.flush()
raw_input()
print(sheet.get_row_values(1))
sys.stdout.flush()
raw_input()
print("Find col 2")
sys.stdout.flush()
raw_input()
print(sheet.get_column_values(2))
sys.stdout.flush()
raw_input()
print("Set B2")
sys.stdout.flush()
raw_input()
sheet.set_cell_value(2, 2, 57)
raw_input()
print("Set range from (1, 1) to (1, 2)")
sys.stdout.flush()
raw_input()
sheet.set_range_values(1, 1, 1, 2, [["Hi", "There"]])
raw_input()
print("Open new sheet...")
sys.stdout.flush()
sheet2 = ss.get_sheet("Sheet2")
print("...and edit it")
sys.stdout.flush()
raw_input()
sheet2.set_range_values(1, 1, 1, 3, [["Brave", "New", "Sheet"]])
raw_input()
print("Can still edit old sheet")
sys.stdout.flush()
raw_input()
sheet.set_cell_value(4, 1, 2015)
raw_input()