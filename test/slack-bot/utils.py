import re 

MENTION_REGEX = "<@(|[WU].+?)>(.*)"

def parse_arguments(msg): 
    '''
    given a string message, return a dictionary where
    keys are arguments, and keys are values 
    '''
    print('(parse_arguments) received {} to parse'.format(msg))

    args = ['-title', '-date', '-guests', '-time', '-len', '-loc', '-alert', '-desc']
    arg_dict = {} 
    indicies = []
    items = msg.split()

    # scan positions of args 
    for i in range(len(items) - 1):
        item = items[i]
        if item in args: 
            indicies.append(i) 
    indicies.append(len(items))
     

    for i in range(len(indicies)-1): 
        cur_arg_index = indicies[i] 
        cur_arg = items[cur_arg_index]
        next_arg_index = indicies[i+1] 
        value = ' '.join(items[cur_arg_index+1:next_arg_index]) 
        arg_dict[cur_arg] = value 

    print('(parse_arguments) output arguments: {}'.format(arg_dict.keys()))

    return arg_dict  


def parse_mentions(msg, remove_dup=True): 
    ''' 
    given a string message, return a list of mentioned people
    returned value will be the id of them 
    '''

    mentions = []
    while(len(msg)): 
        match = re.search(MENTION_REGEX, msg) 
        if match == None:
            return mentions

        mentioned_id = match.group(1)
        print('m_id : ' + mentioned_id)
        mentions.append(mentioned_id)  
        msg = match.group(2) 

    if remove_dup:
        mentions = list(set(mentions))
 
    return mentions

def get_name_by_id(sc, id, token):
    """
    given an id, returns the corresponding id
    """
    users_list = sc.api_call("users.list", token=token) 
    members = users_list["members"]

    for member in members:
        if id == member["id"]:
            return member["name"]
    return None 
    
 
def get_email_by_id(sc, id, token):
    """
    given an id, returns the corresponding email 
    """
    users_list = sc.api_call("users.list", token=token) 
    members = users_list["members"]

    for member in members:
        if id == member["id"]:
            return member["profile"]["email"]

    return None 
    

