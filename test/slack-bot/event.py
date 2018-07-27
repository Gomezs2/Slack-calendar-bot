from utils import get_name_by_id, get_email_by_id
from datetime import datetime, timedelta 
import pytz 

DEFAULT_TITLE = 'Untitled'
DEFAULT_TIME = '08:00 AM'
DEFAULT_LENGTH = 60
DEFAULT_DATE = '-1'
DEFAULT_ALERT = 10
DEFAULT_DESC = ''
DEFAULT_LOC = ''
DEFAULT_GUESTS = []
DEFAULT_GUEST_EMAILS = []
DEFAULT_GUEST_NAMES = []
TIME_ZONE = "America/Los_Angeles"

class EventManager():
    def __init__(self, slack_client, AUTH_TOKEN):
        self.dict = {} 
        self.sc = slack_client
        self.auth_token = AUTH_TOKEN


    def add_event(self, user_id, event):
        emails = []
        for id in event.guests: 
            emails.append(get_email_by_id(self.sc, id, self.auth_token))
        event.guest_emails = emails 
        self.dict[user_id] = event


    def find_event(self, user_id): 
        if user_id in self.dict:
            return self.dict[user_id] 
        else:
            return None 


    def delete_event(self, user_id): 
        if user_id in self.dict: 
            del self.dict[user_id] 



class Event(): 
    def __init__(self, host, host_email, host_name, title=DEFAULT_TITLE, start_time=DEFAULT_TIME, length=DEFAULT_LENGTH, date=DEFAULT_DATE, alert=DEFAULT_ALERT, desc=DEFAULT_DESC, loc=DEFAULT_LOC, guests=DEFAULT_GUESTS, guest_emails=DEFAULT_GUEST_EMAILS, guest_names=DEFAULT_GUEST_NAMES):

        self.title = title
        self.length = length # mins
        
        time_zone = pytz.timezone(TIME_ZONE) 
        today = datetime.now(time_zone) 
        self.time = datetime(year=today.year, month=today.month, day=today.day, hour=0, minute=0, second=0)
        if date is not DEFAULT_DATE:
            self.set_date(date)  
        self.set_time(start_time)  
        self.alert = alert # mins before 
        self.desc = desc # description 
        self.loc = loc # where
        self.host = host
        self.host_email = host_email
        self.host_name = host_name
        self.guests = guests # a list of ids of guests  
        self.guest_emails = guest_emails
        self.guest_names = guest_names


    def export_str(self):
        out = ''
        out += '*title*: ' + self.title
        out += '\n*date*: ' + self.time.strftime('%m/%d/%Y')
        am_pm = 'AM' 
        hh = int(self.time.strftime('%H'))
        if hh > 12: 
            hh -= 12 
            am_pm = 'PM'  
        mm = self.time.strftime('%M')  
        out += '\n*time*: {:02d}:{} {}'.format(hh, mm, am_pm)
        out += '\n*length*: ' + str(self.length) + ' minutes' 
        out += '\n*alert*: before ' + str(self.alert) + ' minutes'
        out += '\n*desc*: ' + self.desc
        out += '\n*location*: ' + self.loc
        
        #if len(self.guest_names) > 1: 
        out += '\n*guests*: ' + ', '.join(self.guest_names)
        #elif len(self.guest_names) == 1:
        #    out += '\n*guests*: ' + self.guest_names[0]
 
        return out


    def set_endtime(self): 
        self.endtime = self.time + timedelta(minutes=self.length)  
        print('(set_endtime) endtime update : {}'.format(self.endtime.strftime('%m/%d/%Y %H:%M:%S'))) 


    def set_guests(self, guests):
        self.guests = guests


    def set_guest_names(self, guest_names):
        self.guest_names = guest_names


    def set_guest_emails(self, guest_emails):
        self.guest_emails = guest_emails

    
    def set_time(self, start_time):
        items = start_time.split() # assume 11:20 AM
        am_pm = items[1]
        items = items[0].split(':') 
        hh = int(items[0]) 
        mm = int(items[1])          
        if am_pm == 'PM':
            hh += 12         
        self.time = self.time.replace(hour=hh, minute=mm, second=0) 
        self.set_endtime()
 
 
    def set_title(self, title):
        self.title = title


    def set_length(self, length):
        self.length = int(length)
        self.set_endtime()


    def set_date(self, date):
        #self.date = date
        items = date.split('/') # assume form like 07/26/2018 for now 
        self.time = self.time.replace(year=int(items[2]), month=int(items[0]), day=int(items[1]))    


    def set_alert(self, alert):
        self.alert = alert


    def set_desc(self, desc):
        self.desc = desc


    def set_loc(self, loc):
        self.loc = loc

