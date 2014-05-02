from random import randint
import math

################### MODEL #############################

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
        self.borders = [[0, 0, 2, 300],
                        [0, 0, 400, 2],
                        [398, 0, 2, 300],
                        [0, 298, 400, 2]]
        self.pellets = [ [randint(10, 380), randint(10, 280), 5, 5] 
                        for _ in range(4) ]
        self.game_over = False
        self.mydir = self.cmd_directions['down']  # start direction: down
        self.mybox = [200, 150, 10, 10]  # start in middle of the screen
        
    def find_closest_pellet(self):
        dist = 9999999

        closest_pellet = None
        for pellet in self.pellets:
            temp_dist = math.hypot(self.mybox[0] - pellet[0], self.mybox[1] - pellet[1])
            if temp_dist < dist:
                dist = temp_dist
                closest_pellet = pellet
        return closest_pellet

    def move_to_pellet(self):

        pellet = self.find_closest_pellet()
        
        cmd = None
        if pellet is not None:
            dist = 99999999
            #direction checker
            if math.hypot((self.mybox[0]-1) - pellet[0], self.mybox[1] - pellet[1]) < dist:
                dist = math.hypot((self.mybox[0]-1) - pellet[0], self.mybox[1] - pellet[1])
                cmd = 'left'
            if math.hypot((self.mybox[0]+1) - pellet[0], self.mybox[1] - pellet[1]) < dist:
                dist = math.hypot((self.mybox[0]+1) - pellet[0], self.mybox[1] - pellet[1])
                cmd = 'right'
            if math.hypot(self.mybox[0] - pellet[0], (self.mybox[1]-1) - pellet[1]) < dist:
                dist = math.hypot(self.mybox[0] - pellet[0], (self.mybox[1]-1) - pellet[1])
                cmd = 'up'
            if math.hypot(self.mybox[0] - pellet[0], (self.mybox[1]+1) - pellet[1]) < dist:
                dist = math.hypot(self.mybox[0] - pellet[0], (self.mybox[1]+1) - pellet[1])
                cmd = 'down'

        return cmd


    def do_cmd(self, cmd):
        if cmd == 'quit':
            self.game_over = True
        else:
            self.mydir = self.cmd_directions[cmd]

    def update(self):
        # move me
        self.mybox[0] += self.mydir[0]
        self.mybox[1] += self.mydir[1]
        # potential collision with a border
        for b in self.borders:
            if collide_boxes(self.mybox, b):
                self.mybox = [200, 150, 10, 10]
        # potential collision with a pellet
        for index, pellet in enumerate(self.pellets):
            if collide_boxes(self.mybox, pellet):
                self.mybox[2] *= 1.2
                self.mybox[3] *= 1.2
                self.pellets[index] = [randint(10, 380), randint(10, 280), 5, 5]
            