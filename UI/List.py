import pygame
import util

class List(object):

    x = 0
    y = 0
    color = (0,0,0)
    highlight_col = (210,210,210)
    aa = True
    width = 1
    height = 1
    item_height = 1
    selected = None
    canSelect = True

    def __init__(self, width, height, font=None, fontsize=12, x = 0, y = 0):
        self.items = []
        self.font = pygame.font.Font(font, fontsize)
        self.item_height = self.font.render("abqplZ!@", self.aa, self.color).get_height()+1
        self.width = width
        self.height = height
        self.x, self.y = x,y

    def setPos(self, x, y):
        self.x, self.y = x,y

    def selectable(self, value):
        self.canSelect = value

    def setColor(self, color=None, highlight_col=None):
        self.color = color if color else self.color
        self.highlight_col = highlight_col if highlight_col else self.highlight_col

    def changeFont(self, font, fontsize):
        self.font = pygame.font.Font(font, fontsize)
        self.item_height = self.font.render("abqplZ!@", self.aa, self.color).get_height()+4
                                     
    def setAA(self, aa):
        self.aa = a
                                     
    def getPoints(self):
        return ((self.x,self.y), (self.x+self.width,self.y), (self.x+self.width,self.y+self.height), (self.x,self.y+self.height))

    def setItems(self,items):
        self.items = list(items)

    def getItems(self):
        return self.items

    def selectItem(self, mpos):
        itemY = mpos[1] - self.y
        noItem = itemY / self.item_height
        if noItem > len(self.items) or noItem == self.selected:
            self.selected = None
        else:
            self.selected = noItem

    def processEvents(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if util.pointInside((event.pos[0], event.pos[1]), self.getPoints()):
                        self.selectItem(event.pos)
                        

    def draw(self, surface, offset=(0,0)):
        sqRect = (self.x,self.y,self.width,self.height)
        pygame.draw.rect(surface, self.color, sqRect, 1)

        x = self.x+2
        y = self.y+2
        width = self.width-4
        for itemNo in xrange(len(self.items)):
            item = self.items[itemNo]
            col = self.color
            if type(item) == tuple:
                col = item[1]
                item = item[0]
            if itemNo == self.selected and self.canSelect:
                pygame.draw.rect(surface, self.highlight_col, (x,y,width,self.item_height))

            surface.blit(self.font.render(item, self.aa, col), (x,y))
            y += self.item_height

    
