import util
import Camera
import pygame
import os

class hud(Camera.Drawable):
    imagesDir = util.IMAGES['HUD']
    posDat = {
        "HEALTH": (7,20),
        "CLIP": (282,11),
        "AMMO": (325,32),
        "DELAY": (350,6),
        "KILLS": (432, 11),
        "DEATHS": (599,11),
        "TEXT": (665, 3)
    }
    _x = 0
    _y = util.CANVAS_HEIGHT - 51

    health = 100
    ammo = 0
    clip = 0
    delay = 50
    kills = 0
    deaths = 0
    text = []

    def __init__(self):
        fontFile = os.path.join(self.imagesDir, "def.ttf")
        self.ammoFont = pygame.font.Font(fontFile, 17)
        self.clipFont = pygame.font.Font(fontFile, 30)
        self.textFont = pygame.font.Font(fontFile, 13)

    def offset(self, offset, y_offset = 0):
        return (offset[0]+self._x, offset[1]+self._y+y_offset)

    def setHealth(self, h): self.health = h
    def setDelay(self, d): self.delay = d
    def setClipAmmo(self, c,a): self.clip,self.ammo = c,a
    def setScore(self, k,d): self.kills,self.deaths = k,d

    def addText(self, text):
        if len(self.text) == 3:
            self.text = self.text[1:] + [text]
        else:
            self.text.append(text)

    def destroy(self):
        del self.ammoFont
        del self.clipFont
        del self.textFont

    def draw(self, surface, offset):
        #outside
        surface.blit(util.IMAGECACHE[os.path.join(self.imagesDir, "hud.png")], (self._x, self._y))
        
        #health
        if self.health > 50:
            fi = "health_green.png"
        elif self.health > 25:
            fi = "health_orange.png"
        else:
            fi = "health_red.png"
        hsf = util.IMAGECACHE[os.path.join(self.imagesDir, fi)]
        newwidth = int(hsf.get_width() * (self.health/100.0))
        surface.blit(hsf, self.offset(self.posDat["HEALTH"]), ( 0,0,newwidth,hsf.get_height()))

        #ammo delay
        dsf = util.IMAGECACHE[os.path.join(self.imagesDir, "delay_bar.png")]
        newheight = int(dsf.get_height() * (self.delay/50.0))
        surface.blit(dsf, self.offset(self.posDat["DELAY"], (dsf.get_height() - newheight)), ( 0, 0, dsf.get_width(), newheight))

        #ammo text
        ammo = self.ammoFont.render("%003d" % self.ammo, False, (0, 0, 0))
        surface.blit(ammo, self.offset(self.posDat["AMMO"]))

        clip = self.clipFont.render("%003d" % self.clip, False, (0, 0, 0))
        surface.blit(clip, self.offset(self.posDat["CLIP"]))

        #score text
        kills = self.clipFont.render("%d" % self.kills, False, (0, 0, 0))
        surface.blit(kills, self.offset(self.posDat["KILLS"]))

        deaths = self.clipFont.render("%d" % self.deaths, False, (0, 0, 0))
        surface.blit(deaths, self.offset(self.posDat["DEATHS"]))

        #text text
        yof = 0
        for text in self.text:
            textsf = self.textFont.render(text, False, (255, 255, 255))
            surface.blit(textsf, self.offset(self.posDat["TEXT"], yof))
            yof += textsf.get_height()+2
        
        
