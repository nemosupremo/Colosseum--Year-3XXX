import pygame
import util
import os
from time import time

class Drawable(object):
    zidx = -1
    def draw(self, surface, offset=(0,0)):
        raise Exception("Draw unimplemented")

    def getRect(self):
        raise Exception("unimplemented")

    def getScreenCenter(self):
        raise Exception("unimplemented")

class Camera(object):
    wireFrame = True
    screen = None
    focusPoint = (0, 0)
    #sprites = [[],[],[],[],[],[],[]]
    sprites = []
    overlay = []
    nums = 0
    focus = None
    SCREEN_HEIGHT = 0
    background = None
    stageImg = None
    stage_w = 0
    stage_h = 0
    i =0
    d =0
    stopDraw = False

    def __init__(self, screen):
        self.screen = screen
        self.SCREEN_HEIGHT = screen.get_height()
        self.sprites = []
        self.overlay = []
        
    def setFocus(self, focus):
        self.focus = focus

    def setFocusPoint(self, point):
        self.focusPoint = point

    def stopDrawing(self):
        self.stopDraw = True

    def continueDrawing(self):
        self.stopDraw = False

    def to_pygame(p):
        """Small hack to convert pymunk to pygame coordinates"""
        return int(p.x), int(self.SCREEN_HEIGHT-p.y)

    def getOffsets(self, focus=None):
        offsetx = 0
        offsety = 0
        
        if focus == None:
            focus = self.focus

        if focus != None:
            c = focus.getCenter()
            offsetx = c[0] - self.focusPoint[0]
            offsety = c[1] - self.focusPoint[1]

        return (offsetx,offsety)

    def setBackground(self, bg, stage_w, stage_h):
        if bg == None: return
        self.BG_MIN_Y =  self.SCREEN_HEIGHT - util.IMAGECACHE[bg].get_height()
        self.BG_MAX_Y = 0
        self.background = bg
        
        self.stage_w = stage_w
        self.stage_h = stage_h

    def setStage(self, stage):
        self.stageImg = stage

    def getScreenPos(self, position, offset):
        return  position[0]-offset[0], position[1]+offset[1]

    def getLensRect(self, proportion=1, focus=None):
        if focus == None: focus = self.focus
        if focus == None:
            return ( (0,0), (self.screen.get_width(), 0), (self.screen.get_width(),self.screen.get_height()), (0,self.screen.get_height()),  (self.screen.get_width()>>1, self.screen.get_height()>>1))
        focus_pos = focus.getScreenCenter()

        top = focus_pos[1] - (self.screen.get_height()*proportion - self.focusPoint[1])
        bottom = focus_pos[1] + (self.screen.get_height()*proportion - self.focusPoint[1])
        left = focus_pos[0] - (self.screen.get_width()*proportion - self.focusPoint[0])
        right = focus_pos[0] + (self.screen.get_width()*proportion - self.focusPoint[0])
        
        return ( (left,top), (right,top), (right,bottom), (left, bottom),  focus_pos)
        

    def inView(self, target, proportion=1, focus=None): # Set Axis Theorem, reduced for rectangles
        if focus == None: focus = self.focus
        lens = self.getLensRect(proportion, focus)
        
        tc = target[4]
        mc = lens[4]
        xprj = -1
        yprj = -1
        mxe = 0
        mye = 0
        txe = 0
        tye = 0
        # (Clockwise from top left)
        # p1, p2, p4, p3
        # p1(0) -- p2(1)
        # p3(3) -- p4(2)
        xprj = target[2][0] - lens[0][0] if tc[0] < mc[0] else lens[2][0] - target[0][0]
        
        if xprj < 0: return False

        yprj = target[2][1] - lens[0][1] if tc[1] < mc[1] else lens[2][1] - target[0][1]
        
        if yprj < 0: return False

        return True
    
    def render(self, focus=None):
        if self.stopDraw: return
        if focus == None: focus = self.focus
        self.screen.fill((255, 255, 255))
        offsetx,offsety = self.getOffsets(focus)

        rendered = 0
        
        if self.background != None and focus != None:
            bg = util.IMAGECACHE[self.background]
            s = time()
            x,y = self.focus.getCenter()
            x,y = self.getScreenPos((0,-(bg.get_height()>>1)+ 50) , (offsetx, offsety))
            x,y = min(0, x),max(y,self.BG_MIN_Y)
            x /= 10
            if x < -bg.get_width():
                x += bg.get_width()*(x/-bg.get_width())
            
            if x + bg.get_width() < self.screen.get_width():
                exsp_x = x + bg.get_width()
                self.screen.blit(bg, (exsp_x,y,self.screen.get_width() - exsp_x,self.screen.get_height()))
            self.screen.blit(bg, (x,y,self.screen.get_width(),self.screen.get_height()))

        if self.stageImg != None:
            st = util.IMAGECACHE[self.stageImg]
            y = offsety - st.get_height() + self.screen.get_height()
            stx = max([0, offsetx])
            sty = max([0, -y])
            self.screen.blit(st, (-offsetx+stx,y+sty), (stx,sty,self.screen.get_width(),self.screen.get_height()))

        for sprite in self.sprites:
            if self.stopDraw: return
            if self.inView(sprite.getRect(), 1.3):
                sprite.draw(self.screen, (offsetx, offsety))

        for overlay in self.overlay:
            if self.stopDraw: return
            overlay.draw(self.screen, None)
        
    def addActor(self, actor, zidx=0):
        if type(actor) == list:
            for act in actor:               
                self.sprites.append(act)
                act.zidx = zidx
                act.surface_height = self.screen.get_height()
                self.nums += 1
        else:
            self.sprites.append(actor)
            actor.zidx = zidx
            actor.surface_height = self.screen.get_height()
            self.nums += 1
        self.sprites.sort(cmp=lambda x,y:x.zidx-y.zidx)

    def removeActor(self, actor):
        try:
            self.sprites.remove(actor)
            self.nums -= 1
        except:
            pass

    def addOverlay(self, overlay):
        self.overlay.append(overlay)

    def removeOverlay(self, overlay):
        self.overlay.remove(overlay)

    def setCursor(self):
        pass
