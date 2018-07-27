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


# Call Calendar API
now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
print('Getting events')
events_result = service.events().list(calendarId='sgomez@atlassian.com', timeMin=now,
                                      maxResults=10, singleEvents=True,
                                      orderBy='startTime').execute()
events = events_result.get('items', [])

##Find events where both people are attendees
targetID = None
if not events:
    print('No upcoming events found.')
for event in events:
	guests = event.get('attendees', [])
	for guest in guests: 
		if(guest['email'] == 'tchoi@atlassian.com'):
			targetID = event['id']
			print('Event ID:', targetID)

   
# Editing - retrieve specific event from the API 
event = service.events().get(calendarId='sgomez@atlassian.com', eventId='qdvp11renci770h8peg8rppcm8').execute()
print('Previous summary:\n' + event['summary'])

event['summary'] = 'Updated title'
event['description'] = 'New description'

#POST request
updated_event = service.events().update(calendarId='sgomez@atlassian.com', eventId=event['id'], body=event, sendNotifications=True).execute()

# Print the updated date.
print(updated_event['summary'])
