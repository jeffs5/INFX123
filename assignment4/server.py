from network import Listener, Handler, poll
 
handlers = {}  # map client handler to user name
users_joined = ""
 
class MyHandler(Handler):
     
    def on_open(self):
        pass
         
    def on_close(self):
    	pass
     
    def on_msg(self, msg):

        if len(msg) == 1:
        	add_client(self, msg)

        elif msg['txt'] == "quit":
        		remove_client(self, msg)

    	else:
    		for handler in handlers.values():
        		if handler != self:
        			handler.do_send(msg['speak'] + ": " + msg['txt'])

def add_client(handler, msg):
	
	global users_joined
	name = msg['join']
	handlers[name] = handler

	if users_joined == "":
		users_joined = name
	else:
		users_joined = users_joined + ", " + name

	for handler in handlers.values():
		handler.do_send(msg['join'] + " joined. Users: " + users_joined)

def remove_client(removed_handler, msg):
	global users_joined

	quiter = msg['user']
	del handlers[quiter]
	users_joined = ""

	for name in handlers.keys():
		if users_joined == "":
			users_joined = name
		else:
			users_joined = users_joined + ", " + name

	for handler in handlers.values():
		if handler != removed_handler:
			handler.do_send(quiter + " left the room. Users: "+ users_joined)
 
port = 8888
server = Listener(port, MyHandler)
running = 1
while running:
	try:
		poll(timeout=0.05)
	except KeyboardInterrupt:
		print "**** Closing server ****"
		for handler in handlers.values():
			handler.do_send("close")
		running = 0