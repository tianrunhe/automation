import pickle
import os.path
import requests
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
RESCUETIME_API_KEY = os.getenv('RESCUETIME_API_KEY')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = 'Sheet1!A2:C'
ACTIVITY_NAME = "Watch TV"


def main():
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    service = build('sheets', 'v4', credentials=credentials)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        durations = []
        row_number = 2
        for row in values:
            time_point = row[0]
            activity_type = row[1]
            logged = len(row) >= 3 and row[2] == 'True'
            if activity_type == 'TV-off':
                duration = durations[-1]
                duration['end_time'] = time_point
            else:
                duration = {'start_time': time_point,
                            'range': f'Sheet1!A{row_number}:C{row_number + 1}',
                            'logged': logged}
                durations.append(duration)

    for duration in [duration for duration in durations if not duration['logged']]:
        response = requests.post(f'https://www.rescuetime.com/anapi/offline_time_post?key={RESCUETIME_API_KEY}',
                                 data={
                                     'start_time': duration['start_time'],
                                     'end_time': duration['end_time'],
                                     'activity_name': ACTIVITY_NAME
                                 })
        if response.status_code != 200:
            print(f"Did not successfully log the duration: {duration}; Error is: {response.reason}")
        else:
            duration['logged'] = True

    for duration in [duration for duration in durations if duration['logged']]:
        value_range_body = {
            "range": duration['range'],
            "values": [
                [duration['start_time'], 'TV-on', 'True'],
                [duration['end_time'], 'TV-off', 'True'],
            ]
        }
        service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=duration['range'],
                                               valueInputOption='USER_ENTERED', body=value_range_body).execute()


if __name__ == '__main__':
    main()
