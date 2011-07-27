import util
import Sprite
import math
from util import box2d
import Weapon
import WeaponLib
import ContactListener
import Network.Structs as Structs
import time
import os
import pygame
import time
import random

class Character(Sprite.Sprite):
    maxSpeed = 10
    maxAirSpeed = 3
    
    speed = .003
    movangle = 0
    InAir = True
    LEFT = -1
    RIGHT = 1
    CharContact = None
    jumping = False
    weapon = None
    weapAngle = 0
    playerId = -1
    bullets = []
    WIREFRAME = False
    sprite = None
    anistate = 'stand'
    mousex = 0
    mousey = 0
    direc = 0
    spriteSize = (0,0)
    screenPos = (0,0)
    charOffset = 0
    bulletPos = (0,0)

    anims = []
    i = 0
    d = None

    health = 100
    delay = 50
    refillTime = 0
    refillDelay = 0
    kills = 0
    deaths = 0
    hud = None
    dead = False
    deadPos = 0
    dietime = 0
    xbound = None
    ybound = None

    pickup = None

    playerName = ""

    drawing = False
    
    def __init__(self, world, isMain, charId = 0, mass = 0, friction = 0, x=(0,0), y=(0,0), managed=False):
        self.sprite = util.PLAYERMAKER.getPlayer(charId)
        self.anistate = 'stand'
        self.spriteSize = self.sprite.calcSize()
        self.charOffset = self.spriteSize.height/2.0
        w,h = self.spriteSize.width, self.spriteSize.height
        self.xbound = x
        self.ybound = y
                
        super(Character, self).__init__(world, {"type":"PERSON", "main":isMain}, w, h, mass, friction, 0 , 0, True, managed)
        self.addShape(self.SHAPES["RECT"])
        #self.getB2Body().SetUserData("CharacterType")
        self.CharContact = CharacterContact(self)
        self.weapon = Weapon.BulletWeapon(util.DEFAULT_WEAPON)
        self.anims = []
        self.i = 0
        self.d = None
        self.health = 100
        self.kills = 0
        self.deaths = 0
        self.bullets = None

        if not managed:
            xpos = random.randint(*self.xbound)/util.SIZERATIO
            ypos = random.randint(*self.ybound)/util.SIZERATIO
            self.getB2Body().transform = ((xpos,ypos), 0)
        

    def setPlayerId(self, pid):
        self.playerId = pid

    def getPlayerId(self):
        return self.playerId

    def setPlayerName(self, name):
        self.playerName = name

    def getPlayerName(self):
        return self.playerName

    def setPlayer(self, sprite):
        self.sprite = sprite

    def getPlayer(self):
        return self.sprite
    
    def makeShapeDef(self):
        pass        

    def setManagedData(self, weaponId, pos, angle, mdist, mang, animation, mainChar):
        self.getB2Body().transform = (pos, angle)
        mp = mainChar.getB2Body().position
        #mousex = pos[0]*util.DRAWRATIO() + mousex
        #mousey = pos[1]*util.DRAWRATIO() + mousey
        mousex = self.screenPos[0] - (mdist * math.cos(mang))
        mousey = self.screenPos[1] - (mdist * math.sin(mang))
        #Sprite.pygame.draw.circle(surface, (255,0,0), (mousex, mousey), 10, 3)
        
        #self.weapon.getB2Body().transform = (pos, gunangle)
        self.anistate = util.PLAYERMAKER.getStateById(animation)
        self.mousex, self.mousey = mousex, mousey
        if weaponId != self.weapon.getWeaponId():
            self.weapon.changeWeapon(weaponId,1)

    def buildNetworkData(self):
        x,y = self.getB2Body().position.x, self.getB2Body().position.y
        rotation = self.movangle
        #mousex = (self.mousex - self.screenPos[0]) + x*util.DRAWRATIO()
        #mousey = (self.mousey - self.screenPos[1]) + y*util.DRAWRATIO()
        mousex = self.sprite.distance(*(self.screenPos+(self.mousex,self.mousey)))
        mousey = math.atan2(self.screenPos[1]-self.mousey, self.screenPos[0]-self.mousex)
        #mousex = self.sprite.distance
        #gunAngle = self.weapAngle
        return Structs.playerDat.pack(0, self.weapon.getWeaponId(), x, y, rotation, mousex, mousey, util.PLAYERMAKER.STATES[self.anistate])

    def linkHud(self, hud):
        self.hud = hud
    
    def mainLoop(self):
        if self.dead:
            self.getB2Body().transform = (self.getB2Body().position, 90)
        else:
            self.getB2Body().transform = (self.getB2Body().position, self.movangle)
        if self.hud != None:
            tme = time.time() 
            if self.dead:
                deathtime = tme - self.dietime
                if deathtime > 3:
                    deathtime -= 3
                    self.health = int(deathtime/5.0 * 100)
                
                if self.health >= 100:
                    self.health = 100
                    self.dead = False
                    self.spawn()
            self.hud.setHealth(self.health)
            self.hud.setScore(self.kills, self.deaths)

            if tme < self.refillTime:
                diff = tme - self.refillTime + self.refillDelay
                self.delay = int((diff/self.refillDelay) * 50)
            else:
                self.delay = 50

            self.hud.setDelay(self.delay)

            self.hud.setClipAmmo(self.weapon.clip, self.weapon.bullets)
            
                
            
        if self.dead:
            sstate = rstate = lstate = 'die_ing' if self.getB2Body().linearVelocity.y != 0 else 'die_end'
        else:
            lstate = 'jump_ing_l' if self.getB2Body().linearVelocity.y != 0 else 'run_l'
            rstate = 'jump_ing_r' if self.getB2Body().linearVelocity.y != 0 else 'run_r'
            sstate = 'jump_ing' if self.getB2Body().linearVelocity.y != 0 else 'stand'
        if self.getB2Body().linearVelocity.x > 0:
            self.anistate = lstate if self.sprite.direc else rstate
        elif self.getB2Body().linearVelocity.x < 0:
            self.anistate = rstate if self.sprite.direc else lstate
        else:
            self.anistate = sstate

    def subHealth(self, health_diff, bulletDirec = False, killerid=-1):
        self.health -= health_diff
        if self.health > 100:
            self.health = 100
        elif self.health <= 0:
            self.die(bulletDirec, killerid)

    def spawn(self):
        xpos = random.randint(*self.xbound)/util.SIZERATIO
        ypos = random.randint(*self.ybound)/util.SIZERATIO
        self.getB2Body().transform = ((xpos,ypos), 0)
        self.weapon.changeWeapon(util.DEFAULT_WEAPON, 80)
        

    def die(self, direction, killerid):
        if not self.dead:
            self.sprite.addNoRepeatState('die_start')
            self.health = 0
            self.deaths += 1
            self.dead = True
            self.dietime = time.time()
            #self.deadPos = self.sprite.direc
            self.sprite.direc = direction
            power = (.015*(-1 if direction else 1),
                    (util.GRAVITY[1] * -.025)/util.SIZERATIO)
            self.getB2Body().ApplyLinearImpulse( power,self.getB2Body().position )
            gc = self.world.getGameClient()
            if gc != None:
                gc.sendDeath(killerid)
        
    def ActionRun(self, direction):

        xvel = self.getB2Body().linearVelocity.x
        maxSpeed = self.maxAirSpeed if self.InAir else self.maxSpeed
        if maxSpeed != 0:
            if direction == self.LEFT:
                if xvel <= maxSpeed*-1:
                    return
            else:
                if xvel >= maxSpeed:
                    return

        imp = (self.speed*direction*math.cos(self.movangle),
               self.speed*direction*math.sin(self.movangle))
        #imp = self.speed*direction, 0
        #print self.getB2Body().GetXForm()
        self.getB2Body().ApplyLinearImpulse( imp, self.getB2Body().position )

    def ActionJump(self):
        if not self.jumping and not self.dead:
            self.jumping = True
            #print (util.GRAVITY[1] * -.025)/util.SIZERATIO
            #power = ((util.GRAVITY[1] * .025)/util.SIZERATIO*math.cos(self.movangle-(math.pi/2)),
            #       (util.GRAVITY[1] * .025)/util.SIZERATIO*math.sin(self.movangle-(math.pi/2)))
            power = (0,
                   (util.GRAVITY[1] * -.025)/util.SIZERATIO)
            #print power
            self.sprite.addNoRepeatState('jump_start')
            self.getB2Body().ApplyLinearImpulse( power,self.getB2Body().position )
            

    def ActionMouse(self, x, y):
        self.mousex = x
        self.mousey = y
        #print self.weapAngle*(180.0/math.pi)

    def ActionShoot(self, x, y, bulletdata = None):
        if self.weapon == None: return
        sound = False
        if bulletdata == None:
            tme = time.time()
            if self.dead:
                return
            if tme < self.refillTime:
                return
            if self.weapon.execute():
                #print "weapon:", self.weapon.getB2Body().position
                sound = True
                self.refillDelay = self.weapon.getDelay()
                self.refillTime = tme + self.refillDelay
                wx,wy = self.bulletPos
                bullet = self.weapon.getBullet(self.world, self,  self.mouseAngle((wx,wy), self.mousex, self.mousey), wx*util.SIZERATIO, wy*util.SIZERATIO, True)
                #self.bullets.append(bullet)
                gc = self.world.getGameClient()
                if gc != None:
                    gc.sendShoot(bullet)
                #self.world.getCamera().setFocus(bullet)
        else:
            bullet = self.weapon.getBullet(self.world, self, bulletdata[3],
                                               bulletdata[1], bulletdata[2], False)
            #self.bullets.append(bullet)

        if WeaponLib.SFX_FIRE[self.weapon.weaponId] != "none" and sound:
            util.SOUNDCACHE[os.path.join(util.SOUNDS['WEAPONS'], WeaponLib.SFX_FIRE[self.weapon.weaponId])+".wav"].play()
        if WeaponLib.FIREFILE[self.weapon.weaponId] != "none":
            fireImgPath = os.path.join(util.IMAGES['EFFECTS'], WeaponLib.FIREFILE[self.weapon.weaponId])
            fireImg = util.IMAGECACHE[fireImgPath]
            fireWidth = fireImg.get_width() / WeaponLib.FIRETILES[self.weapon.weaponId]
            for i in xrange(WeaponLib.FIRETILES[self.weapon.weaponId]):
                if not util.IMAGECACHE.hasImage("%s_%d" % (fireImgPath, i)):
                    subImg = pygame.Surface((fireWidth, fireImg.get_height())).convert()
                    subImg.blit(fireImg, (0, 0), (fireWidth*i, 0, fireWidth, fireImg.get_height()))
                    util.IMAGECACHE["%s_%d" % (fireImgPath, i)] = subImg
            self.anims.append( [-1, WeaponLib.FIRETIME[self.weapon.weaponId], fireWidth, WeaponLib.FIRETILES[self.weapon.weaponId], 0, fireImgPath] )
            
    def ActionReload(self):
        self.weapon.reload()
        self.refillDelay = self.weapon.getReloadDelay()
        self.refillTime = time.time() + self.refillDelay
        self.sprite.addNoRepeatState('reload')
        if WeaponLib.SFX_RELOAD[self.weapon.weaponId] != "none":
            util.SOUNDCACHE[os.path.join(util.SOUNDS['WEAPONS'], WeaponLib.SFX_RELOAD[self.weapon.weaponId])+".wav"].play()
        
    def ActionPickup(self):
        if self.pickup != None:
            if self.pickup.valid:
                if self.pickup.typeId == -1:
                    self.health = min(100, self.health + random.randint(40,75))
                else:
                    self.weapon.changeWeapon(self.pickup.typeId, None)
                gc = self.world.getGameClient()
                if gc != None:
                    gc.sendPicked(self.pickup.serverId)
                self.pickup = None
            
    

    def setPickup(self, pickup):
        #print "set Pickup", pickup
        self.pickup = pickup

    def hasPickup(self):
        return self.pickup != None
    
    def mouseAngle(self, position, xmouse, ymouse):
        offset = self.world.getCameraOffsets()
        #position = self.weapon.getB2Body().position
        swx, swy = (int(position[0]*util.DRAWRATIO())-offset[0], int(self.flipy(position[1]*util.DRAWRATIO())+offset[1]))
        return math.atan2(-1*(ymouse-swy), xmouse-swx)

    def getCharContact(self):
        return self.CharContact

    def destroy(self):
        if self.drawing:
            while self.drawing:
                time.sleep(.1)
        self.CharContact.destroy()
        del self.CharContact
        self.CharContact = None

        super(Character, self).destroy()

        self.sprite = None
        del self.weapon
        self.weapon = None

        self.hud = None
        self.pickup = None

    def draw(self, surface, offset=(0,0)):
        self.drawing = True
        #super(Character, self).draw(surface, offset)
        pos = self.getScreenPos(offset)
        self.screenPos = (pos[0], pos[1] + self.charOffset)
        self.sprite.draw(surface, self.anistate, self.screenPos, self.mousex, self.mousey, self.weapon, self.dead)
        bulletPos = self.sprite.getBulletPos()
        bulletPos = bulletPos[0] + pos[0], bulletPos[1] + pos[1] + self.charOffset
        self.bulletPos = self.inverseScreenPos(bulletPos, offset)
        self.weapAngle = self.sprite.getWeapAngle()

        # The section draws _rotated_ sprites that are added on the end of the gun when it shoots
        for anim in self.anims:
            if anim[4] < time.time():
                anim[0] += 1
                if anim[0] >= anim[3]:
                    anim[0] = 0
                    self.anims.remove(anim)
                    continue
                anim[4] = time.time() + anim[1]/1000.0
            cgfx = util.IMAGECACHE["%s_%d" % (anim[5], anim[0])]

            ox,oy = cgfx.get_width() >> 1, cgfx.get_height() >> 1
            tx,ty = 0, (cgfx.get_height() >> 1)
            dist = (cgfx.get_width() >> 1)#+ anim[0]*anim[2]
            shootAnimAng = -self.weapAngle
            shootPos = list(bulletPos)
            if not self.sprite.direc:
                cgfx = pygame.transform.flip(cgfx, True, False)
                shootAnimAng *= -1
                shootPos = shootPos[0] - math.cos(shootAnimAng)*cgfx.get_width(), shootPos[1] + math.sin(shootAnimAng)*cgfx.get_width()
            graphic = pygame.transform.rotate(cgfx, math.degrees(shootAnimAng))
            newPos = shootPos[0] - ox + dist*math.cos(0+shootAnimAng), shootPos[1] - oy - dist*math.sin(0+shootAnimAng)
            surface.blit(graphic, newPos, None, pygame.BLEND_ADD)
        self.drawing = False

    def __str__(self):
        return "Character Player id: " + str(self.playerId)

class CharacterContact(ContactListener.BaseListener):
    character = None
    quickIgnore = False
    
    def __init__(self, character):
        super(CharacterContact, self).__init__()
        self.character = character
        self.quickIgnore = False

    def BeginContact(self, contact):
        """Called when a contact point is created"""
        if "PERSON" in [contact.fixtureA.body.userData['type'], contact.fixtureB.body.userData['type']]:
            otherShape = contact.fixtureB if (contact.fixtureA.body.userData['type'] == "PERSON") else contact.fixtureA
            #print point
            if otherShape.body.userData['type'] == "GROUND":
                self.character.jumping = False
                self.character.InAir = False
                self.character.movangle = 0#norm+(math.pi/2)
                self.quickIgnore = True
            if otherShape.body.userData['type'] == "PICKUP":
                if otherShape.body.userData['clsRef'].valid and not self.character.hasPickup():
                    self.character.setPickup(otherShape.body.userData['clsRef'])
                

    def EndContact(self, contact):
        """Called when a contact point is removed"""
        if "PERSON" in [contact.fixtureA.body.userData['type'], contact.fixtureB.body.userData['type']]:
            otherShape = contact.fixtureB if (contact.fixtureA.body.userData['type'] == "PERSON") else contact.fixtureA
            if otherShape.body.userData['type'] == "GROUND" and not self.quickIgnore:
                self.character.movangle = 0
                self.character.InAir = True
            elif self.quickIgnore:
                self.quickIgnore = False
            if otherShape.body.userData['type'] == "PICKUP":
                self.character.setPickup(None)
        
    def Add(self, point):
        """Called when a contact point is created"""
        if "PERSON" in [point.shape1.GetBody().GetUserData()['type'], point.shape2.GetBody().GetUserData()['type']]:
            otherShape = point.shape2 if (point.shape1.GetBody().GetUserData()['type'] == "PERSON") else point.shape1
            #print point
            if otherShape.GetBody().GetUserData()['type'] == "GROUND":
                self.character.jumping = False
                # No longer have inclined paths
                #norm = math.atan2(point.normal.y, point.normal.x)
                #norm_ang = math.acos(math.cos(norm))
                self.character.InAir = False
                #if norm_ang > 0 and norm_ang < math.pi:
                self.character.movangle = 0#norm+(math.pi/2)
                    
                    
                self.quickIgnore = True
            #if otherShape.GetBody().GetUserData()['type'] == "PICKUP":
            #    if otherShape.GetBody().GetUserData()['clsRef'].valid:
            #        self.character.setPickup(otherShape.GetBody().GetUserData()['clsRef'])
                

                
    def Persist(self, point):
        """Called when a contact point persists for more than a time step"""
        if "PERSON" in [point.shape1.GetBody().GetUserData()['type'], point.shape2.GetBody().GetUserData()['type']]:
            otherShape = point.shape2 if (point.shape1.GetBody().GetUserData()['type'] == "PERSON") else point.shape1
            if otherShape.GetBody().GetUserData()['type'] == "GROUND":
                self.character.InAir = False
            if otherShape.GetBody().GetUserData()['type'] == "PICKUP":
                if otherShape.GetBody().GetUserData()['clsRef'].valid and not self.character.hasPickup():
                    self.character.setPickup(otherShape.GetBody().GetUserData()['clsRef'])
                
        
    def Remove(self, point):
        """Called when a contact point is removed"""
        if "PERSON" in [point.shape1.GetBody().GetUserData()['type'], point.shape2.GetBody().GetUserData()['type']]:
            otherShape = point.shape2 if (point.shape1.GetBody().GetUserData()['type'] == "PERSON") else point.shape1
            if otherShape.GetBody().GetUserData()['type'] == "GROUND" and not self.quickIgnore:
                self.character.movangle = 0
                self.character.InAir = True
                #print "remove point"
            elif self.quickIgnore:
                self.quickIgnore = False
            if otherShape.GetBody().GetUserData()['type'] == "PICKUP":
                self.character.setPickup(None)
            #print "Remove:", point, "remove"
