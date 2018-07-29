from event import Event  
from utils import parse_arguments, parse_mentions, get_name_by_id, get_email_by_id 
from command import CREATE_COMMAND, ADD_COMMAND, MODIFY_COMMAND, DELETE_COMMAND, INIT_COMMAND, LIST_COMMAND, PUSH_COMMAND, HELP_COMMAND 

def show_help(): 
    msg = '' 
    msg += '`{:^8}` : create an event in the buffer, using following arguments:'.format(CREATE_COMMAND)
    msg += '\n{:^10}`{:^6}` : title of the event.'.format('','-title') 
    msg += '\n{:^10}`{:^6}` : date of the event. (eg. 2018/07/26)'.format('','-date') 
    msg += '\n{:^10}`{:^6}` : start time of the event. (eg. 08:00 AM)'.format('','-time') 
    msg += '\n{:^10}`{:^6}` : duration of the event in minutes. (eg. 60)'.format('','-len') 
    msg += '\n{:^10}`{:^6}` : location/place of the event happening.'.format('','-loc') 
    msg += '\n{:^10}`{:^6}` : alert you before this many minutes. (eg. 10)'.format('','-alert') 
    msg += '\n{:^10}`{:^6}` : description of the event.'.format('','-desc') 
    msg += '\n{:^10}`{:^6}` : guests who you will invite to the event.'.format('','-guests') 
    msg += '\n' 
    msg += "\n{:^10} eg. `create` `-title` Ted's birthday Party `-date` 07/26/2018 `-time` 06:00 PM `-len` 60 `-loc` Ted's house `-alert` 10 `-desc` I can't wait. `-guests` @sergio @taeyeong".format("") 

    msg += '\n'
    msg += '\n`{:^8}` : initialize the buffer by deleting the event that you have created.'.format(INIT_COMMAND) 
    msg += '\n`{:^8}` : add some information to the created event in the buffer. The entered information will overwrite the previous if there was.'.format(ADD_COMMAND)
    msg += '\n`{:^8}` : list your created event that has not been waiting for being pushed in the buffer.'.format(LIST_COMMAND)  
    msg += '\n`{:^8}` : push the event that has been created and waiting in the buffer.'.format(PUSH_COMMAND) 
    msg += '\n' 
    msg += '\n`{:^8}` : access and modify the event that has already been pushed to your Google Calendar account.'.format(MODIFY_COMMAND) 
    msg += '\n`{:^8}` : access and delete the event that has already been pushed to your Google Calendar account.'.format(DELETE_COMMAND) 
    msg += '\n'
    msg += '\n`{:^8}` : show all the available commands.'.format(HELP_COMMAND) 

    return msg


def update_event(em, user_id, msg, all_ids, all_names, user_email='', user_name='', create=False):
    '''
    create an event from the message.  
    and add to event manager  
    '''  
    arg_dict = parse_arguments(msg)
 
    if create:  
        event = Event(user_id, user_email, user_name) 
    else:
        event = em.find_event(user_id)
 
    if '-guests' in arg_dict:  
        guests = parse_mentions(arg_dict['-guests']) 

        # check if valid guests        
        for guest in guests:
            if guest not in all_ids: 
                print("Error invalid guests")
                return em, False 

        # find relevant users' id, email, name
        ids = [] 
        names = []
        for id, name in zip(all_ids, all_names):
            if id in guests:
                ids.append(id)
                names.append(name) 

        # get guest ids and names
        event.set_guests(ids)  
        #event.set_guest_emails(emails)  
        event.set_guest_names(names)  

    if '-title' in arg_dict: 
        event.set_title(arg_dict['-title'])
    
    if '-date' in arg_dict:     
        event.set_date(arg_dict['-date'])

    if '-time' in arg_dict: 
        event.set_time(arg_dict['-time'])

    if '-len' in arg_dict:
        event.set_length(arg_dict['-len'])

    if '-loc' in arg_dict:
        event.set_loc(arg_dict['-loc'])

    if '-alert' in arg_dict:
        event.set_alert(arg_dict['-alert'])

    if '-desc' in arg_dict:
        event.set_desc(arg_dict['-desc'])
   
    em.add_event(user_id, event)  
    return em, True   
