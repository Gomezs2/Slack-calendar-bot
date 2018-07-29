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
	event = service.events().insert(calendarId=host_email, body=eventPackage, sendNotifications=True).execute()
	print('Event created! ID: %s' %(event['id']))
	return event['id'] 


def getEvents(service, organizer, attendee_emails):
	# Call the Calendar API, 'Z' indicates UTC time
	now = datetime.datetime.utcnow().isoformat() + 'Z' 

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
			if(guest['email'] in attendee_emails):
				targetID = event['id']
				found_events.append('Event: %s | ID: %s' %(event['summary'] , targetID) )
	return found_events


def editEvent(service, organizer_email, eventId, fieldsToChange, updated_event):
	#Get event and change
	event = service.events().get(calendarId=organizer_email, eventId=eventId).execute()

	# take care about different fields
	field_translator = {'-title':'summary', '-loc':'location', '-desc':'description', '-alert':'reminders'} 

	# change	
	for field in fieldsToChange.keys():
		if field == '-time' or field == '-len' or field == '-date':
			start = updated_event.time.strftime('%Y-%m-%dT%H:%M:%S')
			end = updated_event.endtime.strftime('%Y-%m-%dT%H:%M:%S')	
			event['start']['dateTime'] = start 
			event['end']['dateTime'] = end   
		else:	
			fieldToChange = field_translator[field]  
			event[fieldToChange] = fieldsToChange[field]  

	updated_event = service.events().update(calendarId=organizer_email, eventId=eventId, body=event, sendNotifications=True).execute()


def deleteEvent(service, organizer_email, eventId):
	service.events().delete(calendarId=organizer_email, eventId=eventId, sendNotifications=True).execute()
	


