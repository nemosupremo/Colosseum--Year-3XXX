import util
from util import box2d
import math
import Sprite
import ContactListener
import WeaponLib
import os
import pygame
import random

"""
class Weapon(Sprite.Sprite):
    w = None
    h = None
    damage = None
    density = None
    sprite = None
    x_offset = None
    y_offset = None
    x = 0
    y = 0
    WEAPONTYPE = {"BULLET":0, "SWORD":1}

    def __init__(self, world):
        super(Weapon, self).__init__(world, {"type":"WEAPON"}, self.w, self.h, 0, 0, self.x, self.y, True)
        self.addShape(self.SHAPES["RECT"], None, True)
    """
             
class SwordWeapon(object):
    radius = None

class BulletWeapon(object):
    force = None
    
    clip = -1
    bullets = 0
    weaponId = 0
    imgInfo = None

    b_w = 10
    b_h = 10
    b_weight = 4
    b_force = 5
    b_time = -1
    b_damage = 10

    def __init__(self, weaponId):
        self.changeWeapon(weaponId, 0)

    def changeWeapon(self, newId, ammo):
        self.weaponId = newId
        if ammo == None: ammo = WeaponLib.CHARGECNT[self.weaponId]*5
        self.spriteInfo = util.WEAPONMAKER.getWeaponImageInfo(self.weaponId)
        self.anistate = 'stand'
        self.spriteSize = self.sprite().get_bounding_rect()
        self.w,self.h = self.spriteSize.width, self.spriteSize.height
        self.clip = WeaponLib.CHARGECNT[self.weaponId] if ammo > WeaponLib.CHARGECNT[self.weaponId] else ammo
        self.bullets = max(0,ammo - self.clip)

    def getWeaponId(self):
        return self.weaponId
    
    def getDelay(self):
        return WeaponLib.DELAY[self.weaponId]/1000.0

    def getReloadDelay(self):
        return WeaponLib.RELOAD[self.weaponId]/1000.0

    def sprite(self):
        return util.WEAPONMAKER.getWeaponImage(self.weaponId)

    def addAmmo(self, ammo):
        self.bullets += ammo

    def isSniper(self):
        return WeaponLib.BULLETTYPE[self.weaponId] == 'sniper'

    def reload(self):
        
        availBullets = WeaponLib.CHARGECNT[self.weaponId] if self.bullets > WeaponLib.CHARGECNT[self.weaponId] else self.bullets
        availBullets -= self.clip
        if availBullets < 0: availBullets = 0
        self.bullets -= availBullets
        self.clip += availBullets

    def execute(self):
        if self.clip <= 0:
            self.clip = 0
            return False
        else:
            self.clip -= 1
            return True

    def getBullet(self, world, shooter, angle, x, y, isOwnerSelf):
        return Bullet(world, self.weaponId, shooter, self.b_weight, self.b_force, angle, self.b_time, self.b_w, self.b_h, x, y, self.b_damage, isOwnerSelf)

class Bullet(Sprite.Sprite):
    w = None
    h = None
    damage = None
    sprite = None
    x = 0
    y = 0
    shooter = None
    WEAPONTYPE = {"BULLET":0, "SWORD":1}
    bulletContact = None

    weight = 1
    force = 1
    angle = 0

    type = 0
    a = True

    weaponId = 0
    isOwnerSelf = False
    shadow = []
    
    def __init__(self, world, weaponId, shooter, weight, force, angle, time, w,h, x, y, damage, isOwnerSelf):
        super(Bullet, self).__init__(world, {"type":"BULLET"}, w, h, weight, 0, x, y, False, True, True, isOwnerSelf)
        self.shooter = shooter
        self.weaponId = weaponId
        self.x = x
        self.y = y
        self.weight = weight
        self.angle = angle
        self.time = time
        self.force = WeaponLib.SPEED[self.weaponId]/4
        self.damage = damage
        self.isOwnerSelf = isOwnerSelf
        self.bulletContact = BulletContact(shooter, self)
        self.world.addContactListener(self.bulletContact)
        self.addShape(self.SHAPES["CIRCLE"], None, True)
        #print "Construct pos", self.getB2Body().GetPosition()
        self.getB2Body().transform = (self.getB2Body().position, self.angle)
        hw = w>>1
        hh = h>>1
        forcePos = (self.getB2Body().position.x + 0*hw*math.cos(self.angle),
                    self.getB2Body().position.y + 0*hw*math.sin(self.angle))
      
        self.shadow = []
        #print forcePos == nforcePos
        #print forcePos
        #print angle
        #self.getB2Body().SetLinearVelocity(shooter.getB2Body().GetLinearVelocity())
        #self.getB2Body().SetAngularVelocity(shooter.getB2Body().GetAngularVelocity())
        #print shooter.getB2Body().GetAngularVelocity()
        self.world.addActor(self)
        self.getB2Body().ApplyForce(self.getVecForce(), forcePos)
        
        """
        dest_angle = math.acos(math.cos((math.atan2( self.getB2Body().GetLinearVelocity().y, self.getB2Body().GetLinearVelocity().x ) - math.pi)));
        src_angle = math.acos(math.cos(self.getB2Body().GetAngle()));
        # Find the shortest variation
        var1 = (math.fabs(dest_angle - src_angle));
        var2 = (math.fabs((dest_angle + math.pi*2) - src_angle));
        var3 = (math.fabs((dest_angle - math.pi*2) - src_angle));

        if (var1 < var2 and var1 < var3):
            self.getB2Body().SetAngularVelocity (( dest_angle - src_angle)  * 1);
        elif (var2 < var1 and var2 < var3):
            self.getB2Body().SetAngularVelocity (( dest_angle + math.pi*2 - src_angle ) * 1);
        elif (var3 < var1 and var3 < var2):
            self.getB2Body().SetAngularVelocity (( dest_angle - math.pi*2 - src_angle) * 1);"""


    def isSniper(self):
        return WeaponLib.BULLETTYPE[self.weaponId] == 'sniper'

    def getVecForce(self):
        xvec = math.cos(self.angle) * self.force
        yvec = math.sin(self.angle) * self.force
        return (xvec, yvec)

    def destroy(self):
        self.bulletContact.destroy()
        del self.bulletContact
        self.bulletContact = None
        self.shadow = []
        super(Bullet, self).destroy()

    def draw(self, surface, offset=(0,0)):
        #super(Bullet, self).draw(surface, offset)
        screenPos = self.getScreenPos(offset)
        #Drawing "BULLET"
        
        if WeaponLib.BULLETFILE[self.weaponId] != "none" :
            boolet = util.IMAGECACHE[os.path.join(util.IMAGES['EFFECTS'], WeaponLib.BULLETFILE[self.weaponId])]
            surface.blit(boolet, screenPos)


        # Drawing "TRACE"
        if WeaponLib.EFFECTFILE[self.weaponId] != "none":
            allef = util.IMAGECACHE[os.path.join(util.IMAGES['EFFECTS'], WeaponLib.EFFECTFILE[self.weaponId])]
            
            subsect = pygame.Rect(0,0*5,100,5)
            graphic = pygame.Surface((subsect.width, subsect.height)).convert()
            graphic.set_colorkey((0,0,0))
            graphic.blit(allef, (0,0), subsect)
            ox,oy = subsect.width>>1, subsect.height>>1
            tx,ty = subsect.width, subsect.height>>1
            dist = ox-tx
            rot = math.atan2(self.getB2Body().linearVelocity.y, self.getB2Body().linearVelocity.x)
            graphic = pygame.transform.rotate(graphic, math.degrees(rot))
            ox,oy = graphic.get_rect().width>>1, graphic.get_rect().height>>1
            
            dx,dy = ox - dist*math.cos(rot), oy + dist*math.sin(rot)

            if self.isSniper():
                self.shadow.append((graphic, (screenPos[0]-dx,screenPos[1]-dy), None, pygame.BLEND_ADD))
                for shadow in self.shadow:
                    surface.blit(*shadow) 
            else:
                surface.blit(graphic, (screenPos[0]-dx,screenPos[1]-dy), None, pygame.BLEND_ADD) 
        

        
        
        
        
class BulletContact(ContactListener.BaseListener):
    shooter = None
    bullet = None

    def __init__(self, character, bullet):
        super(BulletContact, self).__init__()
        self.shooter = character
        self.bullet = bullet

    def BeginContact(self, contact):
        if None in [contact.fixtureA.body.userData, contact.fixtureB.body.userData]: return
        if "BULLET" in [contact.fixtureA.body.userData['type'], contact.fixtureB.body.userData['type']]:
            myShape = contact.fixtureA if (contact.fixtureA.body.userData['type'] == "BULLET") else contact.fixtureB
            otherShape = contact.fixtureB if (contact.fixtureA.body.userData['type'] == "BULLET") else contact.fixtureA
            if myShape.body == self.bullet.getB2Body():
                #print "bullet:", self.bullet.GetB2Body().GetPosition()
                #print [contact.fixtureA.GetBody().GetUserData()['type'], contact.fixtureB.GetBody().GetUserData()['type']]
                if otherShape.body.userData['type'] == "GROUND":
                    #print "bullet died"
                    self.destroy()
                    self.bullet.destroy()
                    
                    
                if otherShape.body.userData['type'] == "PERSON":
                    if otherShape.body != self.shooter.getB2Body():
                        if not self.bullet.isOwnerSelf:
                            if otherShape.body.userData['main'] and self.bullet.isAlive() and not self.bullet.world.gMainChar.dead:
                                randfactor = WeaponLib.RANDFACTOR[self.bullet.weaponId]*100
                                damage = (WeaponLib.DAMAGE[self.bullet.weaponId]/5.0) * (random.randint(int(100-randfactor),int(100+randfactor))/100)
                                direc = self.bullet.getB2Body().linearVelocity.x < 0
                                self.bullet.world.gMainChar.subHealth(damage, direc, self.shooter.getPlayerId())
                        self.destroy()
                        self.bullet.destroy()

    def Add(self, point):
        if None in [point.shape1.GetBody().GetUserData(), contact.fixtureB.GetBody().GetUserData()]: return
        if "BULLET" in [point.shape1.GetBody().GetUserData()['type'], contact.fixtureB.GetBody().GetUserData()['type']]:
            myShape = point.shape1 if (point.shape1.GetBody().GetUserData()['type'] == "BULLET") else point.shape2
            otherShape = point.shape2 if (point.shape1.GetBody().GetUserData()['type'] == "BULLET") else point.shape1
            if myShape.GetBody() == self.bullet.getB2Body():
                #print "bullet:", self.bullet.GetB2Body().GetPosition()
                #print [point.shape1.GetBody().GetUserData()['type'], point.shape2.GetBody().GetUserData()['type']]
                if otherShape.GetBody().GetUserData()['type'] == "GROUND":
                    #print "bullet died"
                    self.destroy()
                    self.bullet.destroy()
                    
                    
                if otherShape.GetBody().GetUserData()['type'] == "PERSON":
                    if otherShape.GetBody() != self.shooter.getB2Body():
                        if not self.bullet.isOwnerSelf:
                            if otherShape.GetBody().GetUserData()['main'] and self.bullet.isAlive() and not self.bullet.world.gMainChar.dead:
                                randfactor = WeaponLib.RANDFACTOR[self.bullet.weaponId]*100
                                damage = (WeaponLib.DAMAGE[self.bullet.weaponId]/5.0) * (random.randint(int(100-randfactor),int(100+randfactor))/100)
                                direc = self.bullet.getB2Body().linearVelocity.x < 0
                                self.bullet.world.gMainChar.subHealth(damage, direc, self.shooter.getPlayerId())
                        self.destroy()
                        self.bullet.destroy()
                        
    
