from __future__ import print_function
import os
import sys
import httplib2


from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
TIME_ZONE = 'Europe/Warsaw'
CALENDAR = 'api-test-calendar'


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
                                   'calendar-python-quickstart.json')
    secret_file_path = os.path.join(credential_dir, CLIENT_SECRET_FILE)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(secret_file_path, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main():
    """Based on basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs inserts or updates
    events according to data from stdin.
    """

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    updated = False

    print("Retrieving calendarID for: %s" % CALENDAR)
    calendar_list = service.calendarList().list().execute()
    for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == CALENDAR:
            calendarId = calendar_list_entry['id']

    print("Retrieving list of events for calendar: %s" % CALENDAR)
    eventsResult = service.events().list(
        calendarId=calendarId, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    for line in sys.stdin.readlines():
        date, admins = line.split('|')
        admins = admins.strip()

        print("Checking if event has already been added to the %s calendar on date %s" % (CALENDAR, date))

        for event in events:
            if event['start']['date'] == date:
                print("Event has already been added to the %s calendar on date %s, updating" % (CALENDAR, date))
                event['summary'] = admins
                updated_event = service.events().update(calendarId=calendarId, eventId=event['id'], body=event).execute()
                updated = True

        if not updated:
            print("Inserting event %s on %s to the %s calendar" % (admins, date, CALENDAR))
            eventBody = {
                'summary': admins,
                'start': {
                    'date': date,
                    'timeZone': TIME_ZONE,
                },
                'end': {
                'date': date,
                'timeZone': TIME_ZONE,
                },
                #'colorId': '1',
            }
            event = service.events().insert(calendarId=calendarId, body=eventBody).execute()

if __name__ == '__main__':
    main()
