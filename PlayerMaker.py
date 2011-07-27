from Players import Players
import XMLHandler
import os
#import math
from math import sqrt, atan2, cos, sin, pi, degrees # 5-10% faster
import pygame
import util
import time
from collections import deque

Z_ORDER = [3,0,1,4,2]

class Frame(object):
    delay = 0
    rect = ()
    sprites = {}
    lastFrame = False
    state =""

    def __init__(self, delay, x1, y1, x2, y2, state):
        self.delay = int(delay)
        self.rect = (int(x1),int(y1),int(x2),int(y2))
        self.sprites = {}
        self.lastFrame = False
        self.state = state

    def addSprite(self, sprite):
        self.sprites[int(sprite['type'])] = (int(sprite['tile']), int(sprite['x']), int(sprite['y']), float(sprite['angle']))

    def isLastFrame(self):
        return self.lastFrame

    def setLastFrame(self, val=True):
        self.lastFrame = val

class Action(object):
    name = ""
    repeat = 0
    events = []
    frames = []
    frame = 0

    def __init__(self, name, repeat):
        self.name = name
        self.repeat = bool(repeat)
        self.events = []
        self.frames = []
        self.frame = 0

    def addEvent(self, event):
        self.events.append(event)

    def addFrame(self, frame):
        if len(self.frames) > 0:
            self.frames[-1].setLastFrame(False)
        self.frames.append(frame)
        frame.setLastFrame()

    def getNextFrame(self):
        if self.frame >= len(self.frames):
            self.frame = 0
        r = self.frames[self.frame]
        self.frame += 1
        return r
        

class Player(object):
    name = ""
    bbfile = ""
    
    headinfo = {}
    arm1info = []
    arm2info = []

    imlib = {}
    loadedIm = {}

    actions = {}

    td = None

    loaded = False
    lastState = None
    lastTime = 0
    lastFrame = None

    noRepeat = None
    inNoRepeat = False

    direc = False

    bullet_out = (0,0)
    weapAngle_out = 0

    def __init__(self, name, bbfile):
        self.name = name
        self.bbfile = bbfile
        self.headinfo = {}
        self.arm1info = []
        self.arm2info = []

        self.imlib = {}
        self.loadedIm = {}

        self.actions = {}
        self.loaded = False
        self.imagesLoaded = False

        self.lastState = 'stand'
        self.lastFrame = None
        self.lastTime = 0

        self.noRepeat = deque([])
        self.inNoRepeat = False

    def all2int(self):
        for k in self.headinfo:
            self.headinfo[k] = int(self.headinfo[k])
        for i in self.arm1info:
            for k in i:
                i[k] = int(i[k])
        for i in self.arm2info:
            for k in i:
                i[k] = int(i[k])

    def calcSize(self, state='stand'):
        return self.draw(None, state, (0,0), 0,0)

    def addNoRepeatState(self, state):
        self.noRepeat.append(state)
            
    def load(self):
        xh = XMLHandler.XMLHandler()
        xh.parse(self.bbfile)
        mapp = xh.getMap()
        #print mapp.getChildren()
        for child in mapp.getChildren():
            if child.name == "headinfo":
                self.headinfo = child.attrs
            elif child.name == "arm1info" or  child.name == "arm2info":
                for info in child.getChildren():
                    if child.name == "arm1info":
                        self.arm1info.append(info.attrs)
                    else:
                        self.arm2info.append(info.attrs)
            elif child.name == "bbinfo":
                for bbinfo in child.getChildren():
                    if bbinfo.name == "images":
                        for image in bbinfo.getChildren():
                            self.imlib[int(image['id'])] = (int(image['tw']), int(image['th']), os.path.join(util.IMAGES['PLAYERS'], image.getData()))
                    if bbinfo.name == "actions":
                        for action in bbinfo.getChildren():
                            act = Action(action['name'], action['repeat'])
                            for data in action.getChildren():
                                if data.name == "events":
                                    for event in data.getChildren():
                                        act.addEvent(event.attrs)
                                elif data.name == "animation":
                                    for frame in data.getChildren():
                                        fram = Frame(frame['ms'], frame['x1'] , frame['y1'],
                                                     frame['x2'], frame['y2'], action['name'])
                                        for sprite in frame.getChildren():
                                            fram.addSprite(sprite)
                                        act.addFrame(fram)
                            self.actions[action['name']] = act
        self.all2int()
        self.loaded = True

    def mouseAngle(self, position, xmouse, ymouse, flip = False):
        swx, swy = (int(position[0]), int(position[1]))
        if flip:
            return -atan2(-1*(ymouse-swy), xmouse-swx)
        else:
            return atan2(-1*(ymouse-swy), xmouse-swx) + pi

    def rotateSurface(self, surface, anchor, rad, area=None):
        if area == None:
            graphic = surface
        else:
            graphic = pygame.Surface((area.width, area.height), pygame.SRCALPHA).convert_alpha()
            graphic.blit(surface, (0,0), area)
        r = graphic.get_rect()
        oldwh = r.width, r.height
        graphic = pygame.transform.rotate(graphic, degrees(rad))
        newwh = graphic.get_rect().width, graphic.get_rect().height
        difwh  = (newwh[0]-r.width)>>1, (newwh[1]-r.height)>>1
        d = self.distance(anchor[0],anchor[1],r.center[0], r.center[1])
        olda = atan2(r.center[1]-anchor[1]+(difwh[1]<<1),abs(r.center[0]-anchor[0]+(difwh[0]<<1)))
        new = ( int(d * cos(rad+olda) + r.center[0] + difwh[0]),  r.height - int(d * sin(rad+olda) + r.center[1]-difwh[1]))
        return (graphic, (new[0], new[1]))

    def distance(self, x1, y1, x2, y2):
        return sqrt((x2-x1)**2 + (y2 - y1)**2)#**.5

    def getBulletPos(self):
        return self.bullet_out

    def getWeapAngle(self):
        return self.weapAngle_out

    def draw(self, surface, state, pos, mousex, mousey, weapon = None, dead = False):
        
        width,height,halfwidth,halfheight=200,200,100,100
        if not self.loaded: self.load()
        
        if time.time() > self.lastTime:
            #Update the frame to be drawn
            if len(self.noRepeat) > 0:
                self.lastState = self.noRepeat.popleft()
                self.inNoRepeat = True
            elif not self.inNoRepeat:   
                self.lastState = state
                
            if not (state == "die_end" and self.lastFrame.isLastFrame() and self.lastFrame.state == "die_end"):
                self.lastFrame = self.actions[self.lastState].getNextFrame()
            self.lastTime = time.time() + self.lastFrame.delay/1000.0

            if self.lastFrame.isLastFrame() and self.inNoRepeat:
                self.inNoRepeat = False

        ret = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()

        flip = self.direc
        if not dead and mousex != None:
            self.direc = flip = pos[0] < mousex
        toRender = {}
        zorder = list(Z_ORDER)
        arm_hand1_hand = (0,0)
        arm_hand1_angle = 0
        
        for im in [3,0,1,2,4]:
            if im == 4:
                if weapon != None and surface:

                    ox,oy = weapon.spriteInfo[1],weapon.spriteInfo[2]
                    tx,ty = weapon.spriteInfo[5],weapon.spriteInfo[6]
                    mx,my = weapon.spriteInfo[3],weapon.spriteInfo[4]
                    
                    trey_d = self.distance(ox,oy,tx,ty)
                    muzz_d = self.distance(ox,oy,mx,my)
                    
                    trey_angle = atan2(oy-ty, ox-tx)
                    
                    graphic, offset = self.rotateSurface(weapon.sprite(), (ox,oy), arm_hand1_angle)#weapon.sprite().get_rect())

                    new_trey = (offset[0] - trey_d * cos(trey_angle-arm_hand1_angle),
                                      offset[1] - trey_d * sin(trey_angle-arm_hand1_angle))

                    new_muzzle = (abs(offset[0] - muzz_d * cos(arm_hand1_angle)),
                                    abs(offset[1] + muzz_d * sin(arm_hand1_angle)))

                    px = arm_hand1_hand[0] - new_trey[0] 
                    py = arm_hand1_hand[1] - new_trey[1] 

                    self.bullet_out = (width-px-new_muzzle[0] if flip else px+new_muzzle[0], py+new_muzzle[1])
                    self.bullet_out = (self.bullet_out[0] - halfwidth, self.bullet_out[1] - halfheight)
                    self.weapAngle_out = mouseangle
                    
                    toRender[im] = (graphic, (px,py))
                    
                else:
                    zorder.remove(4)
                continue
            
            imt = self.imlib[im]
            setdat = self.lastFrame.sprites[im]
            
            graphic = util.IMAGECACHE[imt[2]]
            w,h = graphic.get_width(), graphic.get_height()
            sw,sh = w/imt[0], h/imt[1]
            col,row = setdat[0] % imt[0], int(setdat[0]/imt[0])
            cx,cy = col*sw, row*sh
            area = pygame.Rect(cx, cy, sw, sh)
            offs= (0,0)
            ox,oy = 0,0
            if im in [1,2,3]:
                if im == 1:
                    ex,ey = self.headinfo['eyex'],self.headinfo['eyey']
                    ox,oy = self.headinfo['basex'],self.headinfo['basey']
                elif im == 2:
                    ex,ey = self.arm1info[setdat[0]]['handx'],self.arm1info[setdat[0]]['handy']
                    ox,oy = self.arm1info[setdat[0]]['basex'],self.arm1info[setdat[0]]['basey']
                    bh_d = self.distance(ox,oy,ex,ey)
                    bh_angle = atan2(oy-ey, ox-ex)
                else:
                    ex,ey = self.arm2info[setdat[0]]['handx'],self.arm2info[setdat[0]]['handy']
                    ox,oy = self.arm2info[setdat[0]]['basex'],self.arm2info[setdat[0]]['basey']
                ex += pos[0]
                ey += pos[1] + setdat[2] - (h >> 1)

                mouseangle = self.mouseAngle((ex, ey), mousex, mousey, flip) if (surface and (not dead) and (mousex != None)) else 0
                if state == "die_end" and im == 1:
                    mouseangle = 3.6651914291880923
                    
                graphic, offset = self.rotateSurface(graphic, (ox,oy), mouseangle, area)
                area = graphic.get_rect()
                
            if ox == 0 and oy == 0:
                px = halfwidth - (sw>>1)
                py = halfheight - (sh>>1)
            else:
                px = halfwidth + setdat[1] - offset[0]
                py = halfheight + setdat[2] - offset[1]

                if im == 2:
                    arm_hand1_base = px+offset[0],py+offset[1]
                    arm_hand1_hand = (arm_hand1_base[0] - bh_d * cos(bh_angle-mouseangle),
                                      arm_hand1_base[1] - bh_d * sin(bh_angle-mouseangle))
                    arm_hand1_angle = mouseangle
            toRender[im] = (graphic, (px,py), area)

        for im in zorder:
            ret.blit(*toRender[im])
            
        if flip: ret =  pygame.transform.flip(ret, True, False)
        if surface != None:
            #
            
            surface.blit(ret, (pos[0]-halfwidth, pos[1]-halfheight))
        else:
            return ret.get_bounding_rect()
        
class PlayerMaker(object):
    players = []
    filen = ""
    XML = util.XML['PLAYERS']
    IMAGES = util.IMAGES['PLAYERS']
    STATES = {
        'stand':0,
        'run_l':1,
        'run_r':2,
        'jump_ing_l':3,
        'jump_ing':4,
        'jump_ing_r':5,
        'sit_ing':6,
        'sitwalk':7,
        'boost_left':8,
        'boost_mid':9,
        'boost_right':10,
        'reload':11,
        'die_start':12,
        'die_ing':13,
        'die_end':14
        }
    RSTATES = [
        'stand',
        'run_l',
        'run_r',
        'jump_ing_l',
        'jump_ing',
        'jump_ing_r',
        'sit_ing',
        'sitwalk',
        'boost_left',
        'boost_mid',
        'boost_right',
        'reload',
        'die_start',
        'die_ing',
        'die_end'
        ]
    def __init__(self):
        for player in Players:
            self.players.append((player['name'], os.path.join(self.XML, player['bbfile'])))
        #for player in self.players:
        #    player.load()

    def getPlayer(self, i):
        return Player(*self.players[i])

    def getStateId(self, state):
        return self.STATES[state]

    def getStateById(self, sid):
        return self.RSTATES[sid]
        


        
        
