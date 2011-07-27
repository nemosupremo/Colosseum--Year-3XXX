import pygame
import util

class TextInput(object):

    color = (0,0,0)
    aa = True
    width = 1
    height = 1
    x = 0
    y = 0
    shiftDown = False,False
    lowerNum = ['`','1','2','3','4','5','6','7','8','9','0','-','=']
    upperNum = ['~','!','@','#','$','%','^','&','*','(',')','_','+']
    onEnter = None

    def __init__(self, width, font=None, fontsize=12, x = 0, y = 0):
        self.hasFocus = False
        self.buffer = ""
        self.font = pygame.font.Font(font, fontsize)
        self.width = width
        self.height = self.font.render("abqplZ!@", self.aa, self.color).get_height()+2
        self.x, self.y = x,y

    def setPos(self, x, y):
        self.x, self.y = x,y

    def setEnterFunc(self, func):
        self.onEnter = func

    def setText(self,text):
        self.buffer = text

    def getText(self):
        return self.buffer

    def changeFont(self, font, fontsize):
        self.font = pygame.font.Font(font, fontsize)

    def setColor(self, color):
        self.color = color

    def setAA(self, aa):
        self.aa = aa

    def getPoints(self):
        return ((self.x,self.y), (self.x+self.width,self.y), (self.x+self.width,self.y+self.height), (self.x,self.y+self.height))
        
    def processEvents(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.hasFocus = util.pointInside((event.pos[0], event.pos[1]), self.getPoints())
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT): self.shiftDown = (event.key == pygame.K_LSHIFT or self.shiftDown[0], event.key == pygame.K_RSHIFT or self.shiftDown[1])
                elif event.key == pygame.K_BACKSPACE and self.hasFocus: self.buffer = self.buffer[0:-1]
                elif event.key == pygame.K_RETURN:
                    if self.onEnter != None: self.onEnter()
                elif event.key <= 127 and self.hasFocus:
                    c = chr(event.key)
                    if True in self.shiftDown:
                        if c in self.lowerNum:
                            c = self.upperNum[self.lowerNum.index(c)]
                        else:c = c.upper()
                    self.buffer += c
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    self.shiftDown = (False, self.shiftDown[1])
                elif event.key == pygame.K_RSHIFT:
                    self.shiftDown = (self.shiftDown[0], False)

    def draw(self, surface, offset=(0,0)):
        font_sur = self.font.render(self.buffer, self.aa, self.color)
        sqRect = (self.x,self.y,self.width,font_sur.get_height()+4)
        pygame.draw.rect(surface, self.color, sqRect, 1)
        area = None
        if font_sur.get_width() > self.width:
            area = (font_sur.get_width()-self.width,0,self.width,font_sur.get_height())
        surface.blit(font_sur, (self.x+2,self.y+2), area)

    
