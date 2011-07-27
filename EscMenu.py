import util
import Camera
import pygame
import os

class EscMenu(Camera.Drawable):

    closeRect = pygame.Rect(30,30,245,33)
    leaveRect = pygame.Rect(30,85,245,33)
    changeRect = pygame.Rect(30,135,245,77)
    quitRect = pygame.Rect(30,227,245,33)

    CLICK_CLOSE = 0
    CLICK_LEAVE = 1
    CLICK_CHANGE = 2
    CLICK_QUIT = 3
    
    onClick = None
    
    leaveGame = False
    changeChar = False

    highlight = -1
    x = 0
    y = 0
    
    def __init__(self):
        image = util.IMAGECACHE[os.path.join(util.IMAGES['BUTTONS'], 'escmenu.png')]
        self.x = (util.INTERNAL_WIDTH >> 1) - (image.get_width() >> 1)
        self.y = (util.INTERNAL_HEIGHT >> 1) - (image.get_height() >> 1)
    
    def draw(self, surface, offset):
        if self.highlight == -1:
            image = util.IMAGECACHE[os.path.join(util.IMAGES['BUTTONS'], 'escmenu.png')]
        else:
            image = util.IMAGECACHE[os.path.join(util.IMAGES['BUTTONS'], 'escmenu_%d.png' % self.highlight)] 
        
        surface.blit(image, (self.x,self.y))
        
    def canLeaveGame(self, value):
        self.leaveGame = value

    def canChangeChar(self, value):
        self.changeChar = value

    def getPoints(self, rect):
        return (rect.topleft, rect.topright, rect.bottomright, rect.bottomleft)

    def processEvents(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouseMove((event.pos[0], event.pos[1]))
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouseClick((event.pos[0], event.pos[1]), event.button)

    def setHandler(self, func):
        self.onClick = func

    def mouseClick(self, mousePoint, mouseButton):
        if mouseButton == 1 and self.onClick != None and self.highlight != -1:
            self.onClick(self.highlight)
    
    def mouseMove(self, mousePoint):
        mousePoint = mousePoint[0]-self.x, mousePoint[1]-self.y
        if util.pointInside(mousePoint, self.getPoints(self.closeRect)):
            self.highlight = 0
        elif util.pointInside(mousePoint, self.getPoints(self.leaveRect)) and self.leaveGame:
            self.highlight = 1
        elif util.pointInside(mousePoint, self.getPoints(self.changeRect)) and self.changeChar:
            self.highlight = 2
        elif util.pointInside(mousePoint, self.getPoints(self.quitRect)):
            self.highlight = 3
        else:
            self.highlight = -1
