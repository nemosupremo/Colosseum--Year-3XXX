import WeaponLib
from WeaponImgLib import WeaponImgLib
import os
import math
import pygame
import util
import time


class WeaponMaker(object):
    filen = ""
    #XML = util.XML['WEAPONS']
    IMAGES = util.IMAGES['WEAPONS']
    loaded = []

    def __init__(self):
        self.loaded = [None] * len(WeaponImgLib)
        
    def getWeapon(self, i):
        return WeaponLib

    def getWeaponImage(self, i):
        #if self.loaded[i] == None:
        #    self.loaded[i] = function(os.path.join(self.IMAGES, WeaponImgLib[i][0]))
        #    
        #return self.loaded[i]
        return util.IMAGECACHE[os.path.join(self.IMAGES, WeaponImgLib[i][0])]

    def getWeaponImageInfo(self, i):
        return WeaponImgLib[i]
