from network import Listener, Handler, poll


handlers = {}  # map client handler to user name
names = {} # map name to handler
subs = {} # map tag to handlers

def broadcast(msg):
    for h in handlers.keys():
        h.do_send(msg)


class MyHandler(Handler):
    
    def on_open(self):
        handlers[self] = None
        
    def on_close(self):
        name = handlers[self]
        del handlers[self]
        broadcast({'leave': name, 'users': handlers.values()})
        
    def on_msg(self, msg):
        if 'join' in msg:
            name = msg['join']
            handlers[self] = name
            names[name] = self
            broadcast({'join': name, 'users': handlers.values()})

        elif 'speak' in msg:
            name, txt = msg['speak'], msg['txt']


            #adds subs for tag
            temp = txt.split()

            send_to = []
            for s in temp:
                if '+' in s:
                    temp_word = s.replace('+','', 1)
                    if temp_word not in subs:
                        subs[temp_word] = []
                    subs[temp_word].append(self)
                    send_to.append(self)

            #removes tag for person who sent it
            for s in temp:
                if '-' in s:
                    temp_word = s.replace('-','', 1)
                    if temp_word in subs:
                        for handler in subs[temp_word]:
                            if handler == self:
                                subs[temp_word].remove(self)

            #sends to users subscribed to tag
            for s in temp:
                if '#' in s:
                    temp_word = s.replace('#','', 1)
                    if temp_word in subs:
                        for handler in subs[temp_word]:
                            if handler not in send_to:
                                send_to.append(handler)

            #private message to person
            for s in temp:
                if '@' in s:
                    temp_word = s.replace('@','',1)
                    if temp_word in names:
                        if names[temp_word] not in send_to:
                            send_to.append(names[temp_word])

            
            for h in send_to:
                h.do_send(msg)

Listener(8888, MyHandler)
while 1:
    poll(0.05)