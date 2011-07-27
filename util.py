#import _Box2D #For py2exe
import Box2D as box2d
import pygame
import os
import random

GRAVITY = (0.0,-25.0)
FRAMERATE = 30
INTERNAL_WIDTH = 1024
INTERNAL_HEIGHT = 768
CANVAS_WIDTH = INTERNAL_WIDTH
CANVAS_HEIGHT = INTERNAL_HEIGHT
SIZERATIO = 30.0

DISPLAY_FLAGS = pygame.HWSURFACE|pygame.DOUBLEBUF

w = CANVAS_WIDTH
h = w * 3.0/4.0
if h > CANVAS_HEIGHT: #Wide screen mode
     w = CANVAS_HEIGHT * 4.0/3.0
DRAW_RATIO = w / (INTERNAL_WIDTH/SIZERATIO)

XML_BASE = "./xml"
XML = {
    "PLAYERS" : os.path.join(XML_BASE, "players"),
    "WORLD" : os.path.join(XML_BASE, "mainworld.xml"),
}
IMAGES_BASE = "./images"
IMAGES = {
    "PLAYERS" : os.path.join(IMAGES_BASE, "players"),
    "WEAPONS" : os.path.join(IMAGES_BASE, "weapons"),
    "EFFECTS" : os.path.join(IMAGES_BASE, "effects"),
    "BG" : os.path.join(IMAGES_BASE, "backgrounds"),
    "HUD" : os.path.join(IMAGES_BASE, "hud"),
    "STAGE" : os.path.join(IMAGES_BASE, "stage"),
    "BUTTONS" : os.path.join(IMAGES_BASE, "buttons"),
    "TITLE" : os.path.join(IMAGES_BASE, "title"),
    "LOBBY" : os.path.join(IMAGES_BASE, "lobby"),
    "CHANGECHAR" : os.path.join(IMAGES_BASE, "changechar"),
}
SOUNDS_BASE = "./sounds"
SOUNDS = {
    "WEAPONS" : os.path.join(SOUNDS_BASE, "weapon"),
}

WEAPON_IDS = [0,1,2,3,5,6,8,9,11,12,14,20,22,23,30,34,42,64,65,76]
DEFAULT_WEAPON = 1

from PlayerMaker import PlayerMaker
PLAYERMAKER = PlayerMaker()
PLAYERNAMES = ['Jack', 'Wayne', 'Silver', 'Alex', 'Schwarz 250C',
               'Soul', 'Misty', 'Little J', 'Sue', 'Duncan',
               'Mary', 'Lilica', 'Ami', 'Jackal', 'SIEG',
               'Wolf', 'Luke', 'Don']
from WeaponMaker import WeaponMaker
WEAPONMAKER = WeaponMaker()

from ImageCache import ImageCache
IMAGECACHE = ImageCache()

from SoundCache import SoundCache
SOUNDCACHE = SoundCache()

def WORLDBOUNDS():
    worldAABB=box2d.b2AABB()
    worldAABB.lowerBound = (-1000, -1000)
    worldAABB.upperBound = (1000, 1000)
    return worldAABB

def getXML(xml):
    return os.path.join(XML, xml)

def getFile(typeof, folder, filename):
     return os.path.join(typeof[folder], filename)

def DRAWRATIO():
    return DRAW_RATIO
    w = CANVAS_WIDTH
    h = w * 3.0/4.0
    if h > CANVAS_HEIGHT: #Wide screen mode
        w = CANVAS_HEIGHT * 4.0/3.0
    return w / (INTERNAL_WIDTH/SIZERATIO)

def seedRandom():
     try:
          random.seed(os.urandom(32))
     except:
          random.seed()

def loadImage(image):
     return pygame.image.load(image).convert_alpha()

def loadSound(sound):
     return pygame.mixer.Sound(sound)

def areaTri(p1,p2,p3):
   x0,y0 = p1[0], p1[1]
   x1,y1 = p2[0], p2[1]
   x2,y2 = p3[0], p3[1]
   return (.5)*(x1*y2 - y1*x2 -x0*y2 + y0*x2 + x0*y1 - y0*x1)

def pointInside(point, poly):
     ini = 0;
     for i in range(len(poly)):
          p1 = poly[i]
          p2 = poly[0] if i == len(poly)-1 else poly[i+1]
          p3 = point
          dt = areaTri(p1,p2,p3)
          if abs(dt) == 0: return False
          negpos = dt / abs(dt)
          if ini == 0:
               ini = negpos
          else:
               if negpos != ini: return False
     return True
