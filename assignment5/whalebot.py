from random import randint
from time import sleep
from common import Model

################### CONTROLLER #############################

class Controller():
    def __init__(self, m):
        self.m = m
    
    def poll(self):

        cmd = None
        cmd = self.m.move_to_pellet()
        # cmd = None
        # direction = randint(0, 3)
 
        # if direction == 0:
        #     cmd = 'up'
        # elif direction == 1:
        #     cmd = 'down'
        # elif direction == 2:
        #     cmd = 'left'
        # elif direction == 3:
        #     cmd = 'right'

        # for event in pygame.event.get():  # inputs
        #     if event.type == QUIT:
        #         cmd = 'quit'

        if cmd:
            self.m.do_cmd(cmd)

################### VIEW #############################

class View():
    def __init__(self, m):
        self.m = m
        self.frame_number = 0
        
    def display(self):
        b = self.m.mybox
        if self.frame_number == 50:
            print "Position: " + str(b[0]) + ", " + str(b[1])
            self.frame_number = 0
        self.frame_number += 1
    
################### LOOP #############################

model = Model()
c = Controller(model)
v = View(model)

while not model.game_over:
    sleep(0.02)
    c.poll()
    model.update()
    v.display()