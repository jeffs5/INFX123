from network import Handler, poll
import sys
import os
from threading import Thread
from time import sleep


myname = raw_input('What is your name? ')
running = True

class Client(Handler):
    
    def on_close(self):
        self.do_send({'user': myname, 'txt': 'quit'})
    
    def on_msg(self, msg):
        global running
    	if msg != "close":
        	print msg
        else:
            print "**** Diconnected From Server ****"
            running = False
            os._exit(0)
        
host, port = 'localhost', 8888
client = Client(host, port)
client.do_send({'join': myname})


def periodic_poll():
    while 1:
        poll()
        sleep(0.05)  # seconds
                            
thread = Thread(target=periodic_poll)
thread.daemon = True  # die when the main thread dies 
thread.start()

while running:
    try:
        mytxt = sys.stdin.readline().rstrip()
    	if mytxt == "quit":
    		client.on_close()
    		print "**** Diconnected From Server ****"
    		running = False
    	else:
    		client.do_send({'speak': myname, 'txt': mytxt})

    except KeyboardInterrupt:
        client.on_close()
        exit()
