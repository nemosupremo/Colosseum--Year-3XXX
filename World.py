from util import box2d
import ContactListener
from time import sleep

class World(box2d.b2World):
    gContactListener = None
    gCamera = None
    gGameClient = None
    gMainChar = None
    gDestroyQue = []
    gDestroyed = False
    gActors = []

    def __init__(self, gravity, doSleep):
        self.gContactListener = ContactListener.ContactListener()
        super(World, self).__init__(gravity, doSleep, contactListener=self.gContactListener)
        
        #self.SetContactListener(self.gContactListener)
        self.gDestroyQue = []
        self.gAddQue = []
        self.gBodies = {}
        self.gActors = []
        
    def addContactListener(self, listener):
        self.gContactListener.addListener(listener)

    def removeContactListener(self, listener):
        self.gContactListener.removeListener(listener)

    def setCamera(self, cam):
        self.gCamera = cam

    #def getCamera(self):
    #    return self.gCamera

    def getCameraOffsets(self):
        if self.gCamera == None or self.gDestroyed: return (0,0)
        return self.gCamera.getOffsets()

    def addActor(self, actor):
        if self.gCamera != None:
            self.gActors.append(actor)
            self.gCamera.addActor(actor)

    def removeActor(self, actor):
        if actor in self.gActors and not self.gDestroyed:
            self.gActors.remove(actor)
            self.gCamera.removeActor(actor)

    def setGameClient(self, client):
        self.gGameClient = client

    def getGameClient(self):
        return self.gGameClient

    def setMainCharacter(self, mainChar):
        self.gMainChar = mainChar

    def addNewDynamicBody(self, bodyDef):
        self.gAddQue.append(bodyDef)

    def addDestroyBody(self, body):
        self.gDestroyQue.append(body)

    def destroy(self):
        self.gDestroyed = True
        for actor in self.gActors:
            self.gCamera.removeActor(actor)
            self.gActors.remove(actor)
        del self.gMainChar
        self.gContactListener.clearListeners()
        #self.SetContactListener(None)
        self.contactListener = None
        del self.gContactListener
        self.gCamera = None
        self.gGameClient = None

    def waitForBody(self, bodyDef):
        while True:
            if bodyDef in self.gBodies.keys():
                body = self.gBodies[bodyDef]
                del self.gBodies[bodyDef]
                return body
            sleep(.1)

    def Step(self):
        super(World, self).Step(1.0 / 60, 10, 10)
        super(World, self).ClearForces()
        super(World, self).Step(1.0 / 60, 10, 10)
        super(World, self).ClearForces()
        for bodyDef in self.gAddQue:
            self.gBodies[bodyDef] = self.CreateDynamicBody(bodyDef)
            self.gAddQue.remove(bodyDef)
        for body in self.gDestroyQue:
            if not self.gDestroyed:
                self.gDestroyQue.remove(body)
                body.ClearUserData()
                self.DestroyBody(body)
