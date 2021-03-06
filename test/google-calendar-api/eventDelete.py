from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Calendar API
SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

# Delete
service.events().delete(calendarId='sgomez@atlassian.com', eventId='qdvp11renci770h8peg8rppcm8', sendNotifications=True).execute()
