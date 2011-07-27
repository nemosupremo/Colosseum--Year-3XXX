import pygame
import util
import Sprite
import os
import time

class Pickup(Sprite.Sprite):

    typeId = -1
    serverId = 0
    efxFrameNo = -1
    nxCh = 0
    valid = True

    healthImg = os.path.join(util.IMAGES['EFFECTS'], 'health_pack.png')
    efxImg = os.path.join(util.IMAGES['EFFECTS'], 'item_Effect.png')
    

    def __init__(self, world, tid, serverId, x, y):
        #x,y = (40.8616,2.16167)
        super(Pickup, self).__init__(world, {"type":"PICKUP", "clsRef":self}, 50, 50, 0, 1, x*util.SIZERATIO, y*util.SIZERATIO, True, True, False)
        self.typeId = tid
        self.serverId = serverId
        self.addShape(self.SHAPES["RECT"])

    def destroy(self):
        self.valid = False
        super(Pickup, self).destroy()


    def draw(self, surface, offset):
        if not self.valid:
            self.destroy()
            return
        #super(Pickup, self).draw(surface,offset)
        efx = util.IMAGECACHE[self.efxImg]
        _x = 60*self.efxFrameNo
        self.efxFrameNo += 1
        #if time.time() > self.nxCh:
            
        #    self.nxCh = time.time() + self.delay
        if self.efxFrameNo > 7: self.efxFrameNo = 0

        pos = self.getScreenPos(offset)

        powerUp = None
        if self.typeId == -1:
            powerUp = util.IMAGECACHE[self.healthImg]
        else:
            powerUp = util.WEAPONMAKER.getWeaponImage(self.typeId)

        powerUpPos = pos[0]-(powerUp.get_width()>>1), pos[1]-(powerUp.get_height()>>1)
        efxPos = pos[0]-30, pos[1]-30
        surface.blit(powerUp, powerUpPos)
        surface.blit(efx, efxPos, (_x,0,60,60))
        #pygame.draw.rect(surface, (0,0,0), (pos[0],pos[1],60,60), 3)
        
        

    
