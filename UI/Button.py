import pygame
import util

class Button(object):

    overImg = None
    mainImg = None
    x = 0
    y = 0
    activeImg = None
    onClick = None
    change = False
    visible = True

    def __init__(self, mainImg, overImg, x, y):
        self.mainImg = mainImg
        self.overImg = overImg
        self.width = self.mainImg.get_width()
        self.height = self.mainImg.get_height()
        self.activeImg = self.mainImg
        self.x, self.y = x,y

    def setVisible(self, vis):
        self.visible = vis
    
    def setPos(self, x, y):
        self.x, self.y = x,y

    def getPoints(self):
        return ((self.x,self.y), (self.x+self.width,self.y), (self.x+self.width,self.y+self.height), (self.x,self.y+self.height))
        
    def setOnClick(self, func):
        self.onClick = func
    
    def processEvents(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if util.pointInside((event.pos[0], event.pos[1]), self.getPoints()):
                        if self.onClick != None: self.onClick()
            elif event.type == pygame.MOUSEMOTION:
                if util.pointInside((event.pos[0], event.pos[1]), self.getPoints()) and self.overImg != None:
                    self.activeImg = self.overImg
                    self.change = True
                else:
                    if self.change:
                        self.activeImg = self.mainImg
                        self.change = False

    def draw(self, surface, offset=(0,0)):
        if self.visible: surface.blit(self.activeImg, (self.x,self.y))

    def __del__(self):
        del self.overImg
        del self.mainImg
        del self.activeImg
        self.onClick = None

    
