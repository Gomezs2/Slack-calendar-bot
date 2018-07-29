import os
import time
import re
from slackclient import SlackClient

from utils import parse_mentions, get_email_by_id, get_name_by_id, parse_arguments  
from functions import update_event, show_help
from event import EventManager
from command import CREATE_COMMAND, ADD_COMMAND, MODIFY_COMMAND, DELETE_COMMAND, INIT_COMMAND, LIST_COMMAND, PUSH_COMMAND, HELP_COMMAND

import sys
sys.path.insert(0, '../google-calendar-api')
from main import getService, createEvent, deleteEvent, editEvent  

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
#AUTH_TOKEN = "xoxp-405504331811-405638712146-405402172724-6911eeb1abd04a212f2e0ab6661889f5"
AUTH_TOKEN = "xoxb-405504331811-404929513808-vyzBLNNvgwh0TOqVyYggUxZl" 

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

em = EventManager(slack_client, AUTH_TOKEN)

# google calendar
google_service = getService('token.json', 'credentials.json')


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            sender = event["user"] 
            if user_id == starterbot_id:
                return message, event["channel"], sender 
    return None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(slack_client, sender, command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    global em  
    default_response = "Sorry .. *Sergio* and *Taeyeong* haven't taught me how to respond to your command .. "

    # Finds and executes the given command, filling in response
    response = "" 
   
    # get info about users in channel  
    users_list = slack_client.api_call("users.list", token=AUTH_TOKEN)
    members = users_list["members"] 
    all_ids = [member["id"] for member in members] # extract only names 
    all_names = [member["real_name"] for member in members] # extract only names 
    sender_email = [member["profile"]["email"] for member in members if member['id'] == sender ][0]  
    sender_name = [member["real_name"] for member in members if member['id'] == sender][0] 
    
    # This is where you start to implement more commands!
    if command.startswith(CREATE_COMMAND):

        #### error handling needed for invalid guests 
        em, success = update_event(em, sender, command, all_ids, all_names, user_email=sender_email, user_name=sender_name, create=True)
        event = em.dict[sender]

        # message 
        response += "Creating this event:"
        response += '\n' + event.export_str()
        response += "\n\nIf you want to add more info, please use `{}` command, or if you want to push to your Google Calendar account, use `{}` command.".format(ADD_COMMAND, PUSH_COMMAND) 
    elif command.startswith(ADD_COMMAND):
        event = em.find_event(sender) 
        if event == None: 
            response += "You haven't created any event yet. Use `{}` command first!".format(CREATE_COMMAND)
        else: 
            users_list = slack_client.api_call("users.list", token=AUTH_TOKEN)
            members = users_list["members"] 
            all_ids = [member["id"] for member in members] # extract only names 
            all_names = [member["name"] for member in members] # extract only names 
            em, success = update_event(em, sender, command, all_ids, all_names, create=False)
            event = em.find_event(sender)
            
            response += '\n' + event.export_str()
            response += "\nIf you want to add more info, please use `{}` command.\nIf you want to push to your Google Calendar account, use `{}` command".format(ADD_COMMAND, PUSH_COMMAND) 
 
    elif command.startswith(MODIFY_COMMAND):
        items = command.split()
        if len(items) < 4: 
            response += "You must enter `{}` command, event ID, field to change, and its new value".format(MODIFY_COMMAND)   
        else: 
            arg_to_change = parse_arguments(command) 
            em, success = update_event(em, sender, command, all_ids, all_names, user_email=sender_email, user_name=sender_name, create=True)
            editEvent(google_service, sender_email, items[1], arg_to_change, em.find_event(sender))  
            response += "Event updated."

    elif command.startswith(PUSH_COMMAND):
        event =  em.find_event(sender) 
        if event == None: 
            response += "You haven't created any event yet. Use `{}` command first!".format(CREATE_COMMAND)
        else:  
            event_id = createEvent(google_service, event.title, event.loc, event.desc, event.time, event.endtime, event.host_email, event.guest_emails, event.alert)      
            em.delete_event(sender)
            response += "Your event has been created! The event ID is *{}* you can use to `{}` or `{}`".format(event_id, MODIFY_COMMAND, DELETE_COMMAND)
            response += "\nNow, you don't have any event to `{}`.".format(PUSH_COMMAND) 
 
    elif command.startswith(LIST_COMMAND):
        event = em.find_event(sender) 
        if event == None: 
            response += "You haven't created any event yet. Use `{}` command first!".format(CREATE_COMMAND)
        else: 
            response += '\n' + event.export_str()
            response += "\n\nIf you want to add more info, please use `{}` command, or if you want to push to Google Calendar, use `{}` command.".format(ADD_COMMAND, PUSH_COMMAND) 

    elif command.startswith(INIT_COMMAND):
        em.delete_event(sender)  
        response += "Now, you don't have any event to `{}`.".format(PUSH_COMMAND) 

    elif command.startswith(HELP_COMMAND):
        response += show_help()

    elif command.startswith(DELETE_COMMAND):
        items = command.split() 
        if len(items) != 2: 
            response += "You must enter `{}` command and 1 event ID.".format(DELETE_COMMAND)    
        else: 
            event_id = items[1] 
            deleteEvent(google_service, sender_email, event_id)
            response += "Event deleted."  
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel, sender = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(slack_client, sender, command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")


