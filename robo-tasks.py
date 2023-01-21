from __future__ import print_function
import os.path
from datetime import datetime
import os
import time
import pandas as pd
import schedule
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openpyxl.reader.excel import ExcelReader
from openpyxl.xml import constants as openpyxl_xml_constants
from pandas import ExcelFile
from pandas.io.excel._openpyxl import OpenpyxlReader
import openpyxl

# Install Google API
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib


class OpenpyxlReaderWOFormatting(OpenpyxlReader):
    """OpenpyxlReader without reading formatting
    - this will decrease number of errors and speedup process
    error example https://stackoverflow.com/q/66499849/1731460 """

    def load_workbook(self, filepath_or_buffer):
        """Same as original but with custom archive reader"""
        reader = ExcelReader(filepath_or_buffer, read_only=True, data_only=True, keep_links=False)
        reader.archive.read = self.read_exclude_styles(reader.archive)
        reader.read()
        return reader.wb

    def read_exclude_styles(self, archive):
        """skips adding styles to xlsx workbook , like they were absent
        see logic in openpyxl.styles.stylesheet.apply_stylesheet """

        orig_read = archive.read

        def new_read(name, pwd=None):
            if name == openpyxl_xml_constants.ARC_STYLE:
                raise KeyError
            else:
                return orig_read(name, pwd=pwd)

        return new_read


def emailFilter():
    # Gmail API Scope
    SCOPES = ['https://www.googleapis.com/auth/gmail.settings.basic']

    # Email Acount Setup
    paths = []
    account_name = ['personal-account', 'scott-work-account', 'cafe-account', 'roaster-account']
    for account in account_name:
        paths.append(f'/Users/scott/Learning/Coding/Python3/auto-tasks/credentials/{account}')
    # modify the path to the correct credential folder

    # read blacklist
    ExcelFile._engines['openpyxl_wo_formatting'] = OpenpyxlReaderWOFormatting
    BLACK_LIST = '/Users/scott/Library/CloudStorage/OneDrive-Personal/email-blacklist.xlsx'
    df = pd.read_excel(BLACK_LIST, engine='openpyxl_wo_formatting')
    emails = df['Email Black List'].tolist()

    for path in paths:
        creds = None
        if os.path.exists(f'{path}/token.json'):
            creds = Credentials.from_authorized_user_file(f'{path}/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f'{path}/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(f'{path}/token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            existingfilters = service.users().settings().filters().list(userId='me').execute()
            # list filters
            existingfilter = []
            for item in existingfilters['filter']:
                if 'from' in item['criteria'].keys():
                    existingfilter.append(item['criteria']['from'])
            # check existing filters

            for email in emails:
                if email not in existingfilter:
                    filter_content = {
                        'criteria': {
                            'from': email
                        },
                        'action': {
                            'addLabelIds': ['TRASH'],
                            'removeLabelIds': ['INBOX']
                        }
                    }
                    service.users().settings().filters().create(userId='me', body=filter_content).execute()
                    accountname = path.split('/')[-1]
                    print(f'{email} added to {accountname} blacklist.')

        except HttpError as error:
            print(f'An error occurred: {error}')
    current_time = time.ctime(time.time())
    print(f"Email Blacklist Checked: {current_time}")
    print("----------------------")

def auto_rename():
    """The function helps to automatically rename all tax invoices
        from supplier.pdf to supplier + creation_date.pdf
        invoice folder path setup """
    PATH = '/Users/scott/Library/CloudStorage/OneDrive-Personal/Scott and Coco Pty Ltd/Invoices'

    now = datetime.now()

    # add all files in the folder to the file_array
    file_array = []
    for file in os.listdir(PATH):
        if os.path.isfile(os.path.join(PATH, file)) and file != '.DS_Store':
            file_array.append(file)

    # only rename the file if it doesn't end with number
    # if it ends with a letter, keep it
    for file in file_array:
        test = file.split('.')[0][-1]
        try:
            test = int(test)
        except:
            test

        if type(test) != int:
            old_path = f'{PATH}/{file}'
            # today = date.today().strftime('%d%m%Y')
            creation_date = time.strftime("%d%m%Y", time.strptime(time.ctime(os.path.getmtime(old_path))))
            new_file_name = '.'.join([file.split('.')[0] + ' ' + creation_date,
                                      file.split('.')[1]])  # add date to the file, keep the original suffix
            new_path = f'{PATH}/{new_file_name}'
            uniq = 1
            # avoid mulitple same files on the same day
            while os.path.exists(new_path):
                new_file_name = '.'.join(
                    [file.split('.')[0] + ' ' + creation_date + ' ' + str(uniq), file.split('.')[1]])
                new_path = f'{PATH}/{new_file_name}'
                uniq += 1

            os.rename(old_path, new_path)
            print(f'{file} renamed to {new_file_name} at {now}')

def renameLabels():
    now = datetime.now()
    path = '/Users/scott/Library/CloudStorage/OneDrive-Personal/Scott and Coco Pty Ltd/A - Breeze Valley Coffee Roasters/Shipping Labels'
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)) and file != '.DS_Store':
            files.append(file)


    for file in files:
        test = file.split('.')[0]

        if len(test) > 14:
            old_path = f'{path}/{file}'
            creation_date = time.strftime("%d%m%Y", time.strptime(time.ctime(os.path.getmtime(old_path))))
            new_file_name = '.'.join([creation_date,
                                      file.split('.')[1]])  # add date to the file, keep the original suffix
            new_path = f'{path}/{new_file_name}'
            uniq = 1
            # avoid mulitple same files on the same day
            while os.path.exists(new_path):
                new_file_name = '.'.join(
                    [creation_date + ' ' + str(uniq), file.split('.')[1]])
                new_path = f'{path}/{new_file_name}'
                uniq += 1

            os.rename(old_path, new_path)
            print(f'{file} renamed to {new_file_name} at {now}')

if __name__ == '__main__':
    auto_rename_frequency = 10  # seconds
    email_filter_frequency = 1  # hours

    print(f'Email blacklist filter checking every {email_filter_frequency} hour.')
    print(f'Auto Rename checking every {auto_rename_frequency} seconds.')
    print('Auto Task running at background...')
    schedule.every(email_filter_frequency).hour.do(emailFilter)
    schedule.every(auto_rename_frequency).seconds.do(auto_rename)
    schedule.every(auto_rename_frequency).seconds.do(renameLabels)
    while True:
        schedule.run_pending()
        time.sleep(1)
