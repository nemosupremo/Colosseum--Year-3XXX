import XMLHandler
from util import box2d
import util
import Sprite

class Stage(object):
    bodies = []
    world = None
    MINX = None
    MAXX = None
    width = 0
    height = 0
    stageFile = None

    def __init__(self, world, xmlfile=""):
        self.world = world
        self.bodies = []
        if len(xmlfile) != 0:
            self.fromFile(xmlfile)

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height
    
    def fromFile(self, xmlfile):
        wh = XMLHandler.XMLHandler()
        wh.parse(xmlfile)
        worldDict = wh.getMap()
        #print worldDict
        anchor = worldDict['anchor']
        self.MINX = int(worldDict['minx'])
        self.MAXX = int(worldDict['maxx'])
        self.MINY = int(worldDict['miny'])
        self.MAXY = int(worldDict['maxy'])
        self.height = int(worldDict['height'])
        self.stageFile = worldDict['graphic']
        left = 0
        right = 0
        top = 0
        bottom = 0
        for tile in worldDict.children:
            #print tile
            x,y = int(tile['x']), self.height - int(tile['y']) - int(tile['height'])

            #For stage size calculation
            left = min(left,x)
            right = max(right, x+int(tile['width']))
            top = min(top, y)
            bottom = max(bottom, y+int(tile['height']))
            
            if anchor == 'tl':
                x += int(tile['width'])/2.0
                y += int(tile['height'])/2.0
            tileBody = Sprite.Sprite(self.world, {"type":"GROUND"}, int(tile['width']),
                                     int(tile['height']), 0, int(tile['friction']), x, y)
            verts = []

            if tile['shape'] == "CUSTOM":
                for vert in tile.children:
                    verts.append(int(vert['x']), int(vert['y']))

            
            tileBody.addShape(tileBody.SHAPES[tile['shape']], verts)

            self.bodies.append(tileBody)

        self.width = right - left
        self.height = bottom - top

    def getSprites(self):
        return self.bodies

    def destroy(self):
        for body in self.bodies:
            body.destroy()
        self.world = None
