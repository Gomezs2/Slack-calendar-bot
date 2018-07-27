from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

def getService(token, credentials):
	SCOPES = 'https://www.googleapis.com/auth/calendar'
	store = file.Storage(token)
	creds = store.get()
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets(credentials, SCOPES)
	    creds = tools.run_flow(flow, store)
	return build('calendar', 'v3', http=creds.authorize(Http()))


def createPackage(title, location, desc, start, end, attendees, reminders):
	event = {
	  'summary': title,
	  'location': location,
	  'description': desc,
	  'start': {
	    'dateTime': start,
	    'timeZone': 'America/Los_Angeles',
	  },
	  'end': {
	    'dateTime': end,
	    'timeZone': 'America/Los_Angeles',
	  },
	  'attendees': attendees,
	  'reminders': reminders
	 }
	return event


def createEvent(service, title, location, desc, start, end, host_email, guest_emails, alert):
	#title = raw_input('Title: ')
	#location = raw_input('Location: ')
	#desc = raw_input('Description: ')
	#start = '2018-07-27T16:00:00'
	#end = '2018-07-27T16:45:00'
	start = start.strftime('%Y-%m-%dT%H:%M:%S')  
	end = end.strftime('%Y-%m-%dT%H:%M:%S')  

	attendees = [
		{ 
			'email': host_email,
			'organizer' : True
		}]
	for email in guest_emails: 
		attendees.append({'email': email}) 	
    
	reminders = {
    	'useDefault': False,
    	'overrides': [
    	  {'method': 'popup', 'minutes': alert}
    	]
  	}
	eventPackage = createPackage(title, location, desc, start, end, attendees, reminders)
	#event = service.events().insert(calendarId='sgomez@atlassian.com', body=eventPackage, sendNotifications=True).execute()
	event = service.events().insert(calendarId=host_email, body=eventPackage, sendNotifications=True).execute()
	print('Event created! ID: %s' %(event['id']))
	return event['id'] 

def getEvents(service, organizer, attendee):
	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

	#Gets user's calendar
	events_result = service.events().list(calendarId=organizer, timeMin=now, maxResults=15, singleEvents=True, orderBy='startTime').execute()

	#Get events within user's calendar
	events = events_result.get('items', [])

	##Find events where guest is an attendee
	found_events = []
	targetID = None
	for event in events:
		guests = event.get('attendees', [])
		for guest in guests: 
			if(guest['email'] == attendee):
				targetID = event['id']
				found_events.append('Event: %s | ID: %s' %(event['summary'] , targetID) )
	return found_events


def editEvent(service):
	#Get info
	organizer = 'sgomez@atlassian.com'
	attendee = 'tchoi@atlassian.com'
	events = getEvents(service, organizer, attendee)

	if not events:
		print('No upcoming events found.')
		return
	print('Events to edit:')
	for event in events:
		print(event)

	eventId = raw_input('Please enter the ID of the event you would like to change: ')

	#Need to figure out how let them edit mutliple fields or just one at a time? - what about formatting (time)
	fieldToChange = raw_input('Which field would you like to change?: ')
	newValue = raw_input('New value for %s: ' %(fieldToChange))

	#Get event and change
	event = service.events().get(calendarId=organizer, eventId=eventId).execute()
	print('Changed %s' %(event[fieldToChange]))
	event[fieldToChange] = newValue
	updated_event = service.events().update(calendarId=organizer, eventId=eventId, body=event, sendNotifications=True).execute()
	print('to: %s\nfor %s' %(updated_event[fieldToChange], fieldToChange))


def deleteEvent(service):
	#Get info
	organizer = 'sgomez@atlassian.com'
	attendee = 'tchoi@atlassian.com'
	events = getEvents(service, organizer, attendee)

	if not events:
		print('No events to delete.')
		return

	print('Events to delete:')
	for event in events:
		print(event)

	eventId = raw_input('Please enter the ID of the event you would like to delete: ')

	service.events().delete(calendarId=organizer, eventId=eventId, sendNotifications=True).execute()
	print('Event %s deleted!' %(eventId))

	
'''
# Main
service = getService('token.json', 'credentials.json')
operation = raw_input("What would you like to do (create, edit, delete): ")

if(operation == 'create'):
	createEvent(service)
elif(operation == 'edit'):
	editEvent(service)
elif(operation == 'delete'):
	deleteEvent(service)
else:
	print('Invalid command')
'''




