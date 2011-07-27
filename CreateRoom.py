import util
import pygame
import os
import UI
import Camera

class CreateRoom(Camera.Drawable):

    createRect = pygame.Rect(325,100,140,40)
    roomNameTxt = None
    
    onClick = None

    highlight = -1
    x = 0
    y = 0

    fontObj = None
    nameRendered = None

    width = 500
    height = 150
    title = None

    border = None
    fill = None
    highlight = False
    
    def __init__(self):
        self.x = (util.INTERNAL_WIDTH >> 1) - (self.width >> 1)
        self.y = (util.INTERNAL_HEIGHT >> 1) - (self.height >> 1)
        fontFile = os.path.join(util.IMAGES['HUD'], "def.ttf")
        fontObj = pygame.font.Font(fontFile, 12)
        self.title = fontObj.render("CREATE ROOM", False, (0,0,0))
        self.roomNameTxt = UI.TextInput(450, None, 46, 25+self.x, 50+self.y)
        self.border = pygame.Rect(self.x,self.y,self.width,self.height)
        self.fill = pygame.Rect(self.x+1,self.y+1,self.width-2,self.height-2)
        
        
    def draw(self, surface, offset):
        pygame.draw.rect(surface,(0,0,0),self.border,1)
        pygame.draw.rect(surface,(255,255,255),self.fill,0)
        
        surface.blit(self.title, (self.x+2,self.y+3))
        pygame.draw.line(surface, (0,0,0), (self.x,self.y+16), (self.x+self.width-1,self.y+16))
        pygame.draw.line(surface, (0,0,0), (self.x,self.y+19), (self.x+self.width-1,self.y+19))
        
        cx,cy = self.createRect.left,self.createRect.top
        if self.highlight:
            surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'create_over.png')], (self.x+cx, self.y+cy))
        else:
            surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'create.png')], (self.x+cx, self.y+cy))
            
        self.roomNameTxt.draw(surface,offset)

    def getPoints(self, rect):
        return (rect.topleft, rect.topright, rect.bottomright, rect.bottomleft)

    def processEvents(self, events):
        self.roomNameTxt.processEvents(events)
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouseMove((event.pos[0], event.pos[1]))
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouseClick((event.pos[0], event.pos[1]), event.button)

    def setHandler(self, func):
        self.onClick = func

    def mouseClick(self, mousePoint, mouseButton):
        if mouseButton == 1 and self.highlight:
            self.onClick(self.roomNameTxt.getText())
    
    def mouseMove(self, mousePoint):
        mousePoint = mousePoint[0]-self.x, mousePoint[1]-self.y
        self.highlight = util.pointInside(mousePoint, self.getPoints(self.createRect))
