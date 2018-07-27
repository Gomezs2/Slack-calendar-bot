from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

# Connect to Calendar API
SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

event = {
  'summary': 'Calendar API Testing',
  'location': 'Need to integrate G suite admin API',
  'description': 'Init test',
  'start': {
    'dateTime': '2018-07-27T16:00:00',
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': '2018-07-27T16:45:00',
    'timeZone': 'America/Los_Angeles',
  },
  'attendees': [
  	{
  		'email': 'sgomez@atlassian.com',
  		'organizer' : True
  	},
    {
    	'email': 'tchoi@atlassian.com'
    }
  ],
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'popup', 'minutes': 10}
    ],
  },
 }

#POST Request
event = service.events().insert(calendarId='sgomez@atlassian.com', body=event, sendNotifications=True).execute()
print ('Event created: %s' %(event.get('htmlLink')))