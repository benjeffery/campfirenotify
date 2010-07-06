#!/usr/bin/env python
try:
        import gtk, pygtk, os, os.path, pynotify, pinder, yaml
        pygtk.require('2.0')
except:
        print "Error: need python-notify, pinder, yaml, python-gtk2 and gtk"

import time

config = yaml.load(open('campfire.yml'))

seen_users = {}
def user_name(campfire, user_id):
    if user_id in seen_users:
        return seen_users[user_id]
    else:
        seen_users[user_id] = campfire.user(user_id)['user']['name']
        return seen_users[user_id]

def notify(user, message):
    if not pynotify.init("Urgency"):
        exit()
              
    n = pynotify.Notification(user, message, "file://" + os.path.abspath(os.path.curdir) + "/campfire.gif")
    n.set_urgency(pynotify.URGENCY_LOW)
#    n.set_timeout(1000) # 10 seconds
#    n.set_category("device")
    
    if not n.show():
        print "Failed to send notification"
                                            

if __name__ == "__main__":

    try:
        campfire = pinder.Campfire(config['subdomain'], config['api_key'])
    except:
        print "Cannot Connect to Campfire - check config"
        exit()

    if not config['listen_rooms']:
            print "No rooms listed, these rooms are avaliable:"
            print ', '.join([r['name'] for r in campfire.rooms()])
            exit()
    if config['listen_rooms'] == 'all':
        listen_rooms = [campfire.find_room_by_name(room['name']) for room in campfire.rooms()]
    else:
        listen_rooms = [campfire.find_room_by_name(r['name']) for r in campfire.rooms() if r['name'] in config['listen_rooms']]
    if not listen_rooms:
        print "No rooms to listen to"

    print 'Getting up to date'
    seen_messages = set()
    for room in listen_rooms:
        seen_messages.update(t['id'] for t in room.transcript())
    print '...done'
    while True:
        print 'Sleeping'
        time.sleep(config['period'])
        print 'Checking'
        messages = [m for room in listen_rooms for m in room.transcript()]
        new_messages = [m for m in messages if m['id'] not in seen_messages and m['type'] == 'TextMessage']
        seen_messages.update(t['id'] for t in new_messages)
        print len(new_messages), 'new messages'
        for message in new_messages:
            name = user_name(campfire, message['user_id'])
            if name not in config['user_blacklist'] and any(word.lower() in message['body'] for word in config['trigger_words']):
                notify(name, str(message['body']))

    
        
