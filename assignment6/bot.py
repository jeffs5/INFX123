from random import choice, randint
from threading import Thread
from network import Handler, poll
from pygame import Rect
from pygame.event import get as get_pygame_events
from pygame.time import Clock
from pygame.display import set_mode, update as update_pygame_display
from pygame.draw import rect as draw_rect
import math
import sys


################### MODEL ##################################

def collide_boxes(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return x1 < x2 + w2 and y1 < y2 + h2 and x2 < x1 + w1 and y2 < y1 + h1
    

class Model():
    
    cmd_directions = {'up': (0, -1),
                      'down': (0, 1),
                      'left': (-1, 0),
                      'right': (1, 0)}
    
    def __init__(self):
        self.prevbox = []
        self.mybox = []
        self.game_over = False
        self.borders = []
        self.pellets = []
        self.players = {}  # map player name to rectangle
        self.myname = None
 
class NetworkController(Handler):

    def __init__(self, model):
        Handler.__init__(self, 'localhost', 8888)   # connect asynchronously
        self.model = model
        # print 'Client created'


    def make_rect(self,quad):  # make a pygame.Rect from a list of 4 integers; used to parse incoming messages
        x, y, w, h = quad
        return Rect(x, y, w, h)


    # updates model
    def on_msg(self, data):
        self.model.borders = [self.make_rect(b) for b in data['borders']]
        self.model.pellets = [self.make_rect(p) for p in data['pellets']]
        self.model.players = {name: self.make_rect(p) for name, p in data['players'].items()}
        self.model.myname = data['myname']
        self.model.prevbox = self.model.mybox
        self.model.mybox = self.model.players[self.model.myname]
        # print '###############'
        # print self.model.prevbox
        # print self.model.mybox 
        # print '###############'
        if self.model.prevbox:
            if not self.model.prevbox[2] == self.model.mybox[2] and not self.model.mybox[2] == 10:
                # print self.model.prevbox
                # print self.model.mybox
                print 'Pellet eaten!'

    def on_open(self):
        print 'Client connected'
        self.do_send({'input' : 'down'})
        
    def on_close(self):
        print 'Server closed'
        self.model.game_over = True


    def send_network(self, cmd):
        self.cmds = ['up', 'down', 'left', 'right']
        poll()
        if cmd in self.cmds:

            msg = cmd
            self.do_send({'input' : msg})

################### CONTROLLER #############################

class RandomBotController():
    def __init__(self, m):
        self.m = m
        self.cmds = ['up', 'down', 'left', 'right']
        
    def poll(self):
        self.m.do_cmd(choice(self.cmds))
        
################### CONTROLLER #############################

#doesn't completely work
class SmartBotController():
    def __init__(self, m):
        self.m = m
        
    def poll(self):
        if self.m.pellets:
            p = self.m.pellets[0]  # always target the first pellet
            b = self.m.mybox
            if p[0] > b[0]:
                cmd = 'right'
            elif p[0] < b[0]: # p[2] to avoid stuttering left-right movement
                cmd = 'left'
            elif p[1] > b[1]:
                cmd = 'down'
            else:
                cmd = 'up'

            return cmd
        return 'loading'

################### CONTROLLER #############################

class CustomBotController():
    def __init__(self, m):
        self.m = m
    
    def find_closest_pellet(self):
        dist = 9999999

        closest_pellet = None
        for pellet in self.m.pellets:
            temp_dist = math.hypot(self.m.mybox[0] - pellet[0], self.m.mybox[1] - pellet[1])
            if temp_dist < dist:
                dist = temp_dist
                closest_pellet = pellet
        return closest_pellet

    def move_to_pellet(self):

        p = self.find_closest_pellet()
        b = self.m.mybox
        
        cmd = 'down'
        if p is not None:
            dist = 99999999
            #direction checker
            if math.hypot((b[0]-1) - p[0], b[1] - p[1]) < dist:
                dist = math.hypot((b[0]-1) - p[0], b[1] - p[1])
                cmd = 'left'
            if math.hypot((b[0]+1) - p[0], b[1] - p[1]) < dist:
                dist = math.hypot((b[0]+1) - p[0], b[1] - p[1])
                cmd = 'right'
            if math.hypot(b[0] - p[0], (b[1]-1) - p[1]) < dist:
                dist = math.hypot(b[0] - p[0], (b[1]-1) - p[1])
                cmd = 'up'
            if math.hypot(b[0] - p[0], (b[1]+1) - p[1]) < dist:
                dist = math.hypot(b[0] - p[0], (b[1]+1) - p[1])
                cmd = 'down'

        return cmd

    def poll(self):

        if self.m.pellets:
            cmd = self.move_to_pellet()

            return cmd
        return 'loading'


################### CONSOLE VIEW #############################

class ConsoleView():
    def __init__(self, m):
        self.m = m
        self.frame_freq = 20
        self.frame_count = 0
        
    def display(self):
        self.frame_count += 1
        if self.frame_count == self.frame_freq:
            self.frame_count = 0
            if self.m.mybox:
                b = self.m.mybox
                # print 'Position: %d, %d' % (b[0], b[1])


################### PYGAME VIEW #############################
# this view is only here in case you want to see how the bot behaves

import pygame

class PygameView():
    
    def __init__(self, m):
        self.m = m
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))

        
    def display(self):
        pygame.event.pump()
        screen = self.screen
        borders = [pygame.Rect(b[0], b[1], b[2], b[3]) for b in self.m.borders]
        pellets = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in self.m.pellets]
        if self.m.players:
            b = self.m.players[self.m.myname]
            myrect = pygame.Rect(b[0], b[1], b[2], b[3])
        screen.fill((0, 0, 64))  # dark blue

        if self.m.players:
            pygame.draw.rect(screen, (0, 191, 255), myrect)  # Deep Sky Blue
        [pygame.draw.rect(screen, (255, 192, 203), p) for p in pellets]  # pink
        [pygame.draw.rect(screen, (0, 191, 255), b) for b in borders]  # red

        if self.m.players:
            for name, p in self.m.players.items():
                if name != self.m.myname:
                    draw_rect(screen, (255, 0, 0), p)  # red
            if self.m.myname:
                draw_rect(screen, (0, 191, 255), self.m.players[self.m.myname])  # deep sky blue

        pygame.display.update()
        
################### LOOP #############################

model = Model()
n = NetworkController(model)
#c = SmartBotController(model)
c = CustomBotController(model)
#v = PygameView(model)
v2 = ConsoleView(model)
clock = Clock()

while not model.game_over:
    clock.tick(50)
    cmd = c.poll()
    n.send_network(cmd)
    #model.update() # updates on messages received 
    #v.display()
    v2.display()