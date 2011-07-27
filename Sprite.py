import pygame
from util import box2d
import util
import math
import Camera

class Sprite(Camera.Drawable):
    body = None
    sprite = None
    mass = 0
    friction = 0
    size = (0,0)
    color = (255,255,255)
    name = ""
    world = None
    surfaceHeight = util.CANVAS_HEIGHT
    DRAW_RATIO = 0
    sensor = False
    alive = True
    SHAPES = {
        "RECT" : 0,
        "CIRCLE" : 1,
        "RTLEFT" : 2,
        "RTRIGHT" : 3,
        "CUSTOM" : 4
    }
    destroyable = True

    def __init__(self, world, data, w, h=None, mass = 0, friction = 0, x=0, y=0, fixedRotation = False, sensor = False, bullet = False, mainThread=True):
        self.size = (w,h)
        self.mass = mass
        self.friction = friction
        self.sensor = sensor
        
        """ BOX 2D """
        
        self.world = world
        bodyDef = box2d.b2BodyDef()
        bodyDef.position = (x/util.SIZERATIO,y/util.SIZERATIO)
        bodyDef.fixedRotation = fixedRotation
        bodyDef.isBullet = bullet
        if mainThread:
            self.body = self.world.CreateBody(bodyDef) if mass == 0 else self.world.CreateDynamicBody(position=(x/util.SIZERATIO,y/util.SIZERATIO), fixedRotation=fixedRotation, isBullet=bullet)
            self.body.userData = data
        else:
            self.world.addNewDynamicBody(bodyDef)
            self.body = self.world.waitForBody(bodyDef)
            self.body.userData = data

        w = util.CANVAS_WIDTH
        h = w / (4.0/3.0)

        #self.DRAW_RATIO = w / (util.INTERNAL_WIDTH/util.SIZERATIO)
        #(w*h) / ((*util.INTERNAL_HEIGHT)/util.SIZERATIO)
        #shapeDef = box2d.b2PolygonDef()
        #shapeDef.SetAsBox(w/2.0/util.SIZERATIO, h/2.0/util.SIZERATIO)
        #shapeDef.density = float(mass) / (w*h)
        #shapeDef.friction = friction
        
        #self.body.CreateShape(shapeDef)
        #self.body.SetMassFromShapes()

    def mainLoop(self):
        pass

    def isAlive(self):
        return self.alive

    def destroy(self):
        if self.destroyable:
            self.destroyable = False
            self.alive = False
            self.world.removeActor(self)
            self.body.ClearUserData()
            self.world.addDestroyBody(self.body)
            self.body = None
            self.world = None
        
    def addShapeDef(self, shapeDef):
        self.body.CreateShape(shapeDef)
        self.body.SetMassFromShapes()

    def getSize(self):
        return self.size
        
    def addShape(self, shape, verts = None, sensor = False):
        w,h = self.size
        shapeDef = None
        fixtureDef = None
        if shape == self.SHAPES["RECT"]:
            fixtureDef = box2d.b2FixtureDef()
            shapeDef = box2d.b2PolygonShape()
            shapeDef.SetAsBox(w/2.0/util.SIZERATIO, h/2.0/util.SIZERATIO)
            fixtureDef.density = float(self.mass) / (w*h)
            fixtureDef.friction = self.friction
            fixtureDef.restitution = .1
        elif shape == self.SHAPES["CIRCLE"]:
            fixtureDef = box2d.b2FixtureDef()
            shapeDef = box2d.b2CircleShape()
            shapeDef.radius = w/util.SIZERATIO
            fixtureDef.friction = self.friction
            fixtureDef.density = float(self.mass) / (math.pi*(w**2))
            fixtureDef.restitution = .1
        elif shape == self.SHAPES["RTLEFT"]:
            fixtureDef = box2d.b2FixtureDef()
            shapeDef = box2d.b2PolygonDef()
            verts = (
                ((w/util.SIZERATIO/2.0),(h/util.SIZERATIO/2.0)),
                (-(w/util.SIZERATIO/2.0),-(h/util.SIZERATIO/2.0)),
                ((w/util.SIZERATIO/2.0),-(h/util.SIZERATIO/2.0)),
            )
            shapeDef.setVertices(verts)
            shapeDef.vertexCount = 3
            fixtureDef.density = float(self.mass) / (w*h*.5)
            fixtureDef.friction = self.friction
            fixtureDef.restitution = .1
        elif shape == self.SHAPES["RTRIGHT"]:
            fixtureDef = box2d.b2FixtureDef()
            shapeDef = box2d.b2PolygonShape()
            verts = (
                (-(w/util.SIZERATIO/2.0),(h/util.SIZERATIO/2.0)),
                (-(w/util.SIZERATIO/2.0),-(h/util.SIZERATIO/2.0)),
                ((w/util.SIZERATIO/2.0),-(h/util.SIZERATIO/2.0)),
            )
            shapeDef.setVertices(verts)
            shapeDef.vertexCount = 3
            fixtureDef.density = float(self.mass) / (w*h*.5)
            fixtureDef.friction = self.friction
            fixtureDef.restitution = .1
        else:
            shapeDef.setVertices(verts)
            shapeDef.vertexCount = len(verts)
            fixtureDef.density = float(self.mass) / (w*h)
            fixtureDef.friction = self.friction
            fixtureDef.restitution = .1

        fixtureDef.isSensor = sensor or self.sensor
        fixtureDef.shape = shapeDef
        self.body.CreateFixture(fixtureDef)
        #self.body.CreateShape(shapeDef)
        #self.body.SetMassFromShapes()

    def getB2Body(self):
        return self.body

    def __del__(self):
        del self.body

    #def position(self):
    #    return (self.body.position.x*util.SIZERATIO, self.body.position.y*util.SIZERATIO)

    #def screenPosition(self, surface):
    #    return (int(self.body.position.x*util.SIZERATIO), (surface.get_height() - int(self.body.position.y*util.SIZERATIO)))

    def flipy(self, y):
        return self.surfaceHeight - y 

    def getCenter(self):
        if self.body == None: return (0,0)
        return (int(self.body.position.x*util.DRAWRATIO()), int(self.body.position.y*util.DRAWRATIO()))

    def getScreenCenter(self):
        if self.body == None: return (0,0)
        return (int(self.body.position.x*util.DRAWRATIO()), int(self.flipy(self.body.position.y*util.DRAWRATIO())))

    # Clock wise from top left
    def getRect(self):
        cen = self.getScreenCenter()
        w,h = self.size
        if h == None: #h is radius of a circle
            w = h = w << 1
        hw = w >> 1
        hh = h >> 1
        return ( (cen[0] - hw, cen[1] - hh ), (cen[0] + hw, cen[1] - hh ), (cen[0] + hw, cen[1] + hh ), (cen[0] - hw, cen[1] + hh ), cen )
        
    def getScreenPos(self, offset):
        position = self.body.position
        return  (int(position.x*util.DRAWRATIO())-offset[0], int(self.flipy(position.y*util.DRAWRATIO())+offset[1]))

    def inverseScreenPos(self, position, offset):
        return  ((position[0]+offset[0])/util.DRAWRATIO(), -( (position[1]-offset[1]-self.surfaceHeight) / util.DRAWRATIO() ))
        
    def draw(self, surface, offset=(0,0)):
        w,h = self.size
        if True:
            points = []
            for shape in self.body.GetShapeList():
                shapeType = shape.GetType()
                if shapeType == box2d.e_circleShape:
                    position = self.body.GetWorldPoint(shape.GetLocalPosition())
                    pos = (int(position.x*util.DRAWRATIO())-offset[0], int(self.flipy(position.y*util.DRAWRATIO())+offset[1]))
                    pygame.draw.circle(surface, (0,0,0), pos, int(shape.radius*util.DRAWRATIO()), 2) 
                    #print pos
                else:
                    for p in shape.getVertices_b2Vec2():
                        p = self.body.GetWorldPoint(p)
                        x,y = int(p.x*util.DRAWRATIO()), int(p.y*util.DRAWRATIO())
                        points.append(((x-offset[0]), self.flipy(y)+offset[1]))
                        
                    if points[-1] != points[0]:
                        points.append(points[0])

                    pygame.draw.polygon(surface, self.color, points, 0) 
                    for p in points:
                        for p2 in points:
                            if p == p2:
                                continue
                            pygame.draw.line(surface, (0, 0, 0), p, p2)


        
        
    
