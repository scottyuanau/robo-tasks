import os
from datetime import datetime
def logMSG(message):
    # log file path
    path = '/Users/scott/Library/CloudStorage/OneDrive-Personal/log.log'
    now = datetime.now()
    if not os.path.exists(path):
        with open(path, 'w') as f:
            print(f'{now}: {message}')
            print(f'{now}: {message}', file=f)
    else:
        with open(path, 'a') as f:
            print(f'{now}: {message}')
            print(f'{now}: {message}', file=f)

logMSG('just a test3')