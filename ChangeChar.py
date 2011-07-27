import util
import pygame
import os
import Camera

class ChangeChar(Camera.Drawable):

    selectRect = pygame.Rect(164,299,138,39)
    leftTri = ( (53, 266), (53,330), (21,298) )
    rightTri = ( (345, 266), (377,298), (345,330) )
    
    onClick = None

    highlight = -1
    x = 0
    y = 0

    charId = 0
    fontObj = None
    nameRendered = None
    sprite = None
    
    def __init__(self, charId):
        image = util.IMAGECACHE[os.path.join(util.IMAGES['CHANGECHAR'], 'change.png')]
        self.x = (util.INTERNAL_WIDTH >> 1) - (image.get_width() >> 1)
        self.y = (util.INTERNAL_HEIGHT >> 1) - (image.get_height() >> 1)
        self.charId = charId
        fontFile = os.path.join(util.IMAGES['HUD'], "def.ttf")
        self.fontObj = pygame.font.Font(fontFile, 12)
        self.changeChar(self.charId)
        

    def changeChar(self, charId):
        self.charId = charId
        pname = util.PLAYERNAMES[self.charId]
        self.nameRendered = self.fontObj.render("Name: "+pname, False, (0, 0, 0))
        self.sprite = util.PLAYERMAKER.getPlayer(self.charId)
        
        
    def draw(self, surface, offset):
        if self.highlight == -1:
            image = util.IMAGECACHE[os.path.join(util.IMAGES['CHANGECHAR'], 'change.png')]
        else:
            image = util.IMAGECACHE[os.path.join(util.IMAGES['CHANGECHAR'], 'change_%d.png' % self.highlight)] 
        
        surface.blit(image, (self.x,self.y))
        surface.blit(self.nameRendered, (self.x+21, self.y+244))
        self.sprite.draw(surface, 'stand', (self.x+200, self.y+230), None, None, None, False)

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
        if mouseButton == 1 and self.highlight != -1:
            if self.highlight == 0:
                self.charId -= 1
                if self.charId == -1: self.charId = len(util.PLAYERNAMES) - 1
                self.changeChar(self.charId)
            elif self.highlight == 1:
                self.charId += 1
                if self.charId == len(util.PLAYERNAMES): self.charId = 0
                self.changeChar(self.charId)
            elif self.highlight == 2:
                self.onClick(self.charId)
    
    def mouseMove(self, mousePoint):
        mousePoint = mousePoint[0]-self.x, mousePoint[1]-self.y
        if util.pointInside(mousePoint, self.leftTri):
            self.highlight = 0
        elif util.pointInside(mousePoint, self.rightTri):
            self.highlight = 1
        elif util.pointInside(mousePoint, self.getPoints(self.selectRect)):
            self.highlight = 2
        else:
            self.highlight = -1
