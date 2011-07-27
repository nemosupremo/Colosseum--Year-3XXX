from util import box2d

class ContactListener(box2d.b2ContactListener):
    listeners = []

    def __init__(self):
        super(ContactListener, self).__init__()
        self.listeners = []

    def BeginContact(self, contact):
        if None in [contact.fixtureA.body.userData,
                    contact.fixtureB.body.userData]:
            return
        for listener in self.listeners:
            if self.testListener(listener): continue
            listener.BeginContact(contact)

    def EndContact(self, contact):
        if None in [contact.fixtureA.body.userData,
                    contact.fixtureB.body.userData]:
            return
        for listener in self.listeners:
            if self.testListener(listener): continue
            listener.EndContact(contact)

    def PreSolve(self, contact, oldManifold):
        pass

    def PostSolve(self, contact, impulse):
        pass

    """def Add(self, point):
        if None in [point.shape1.GetBody().GetUserData(),
                    point.shape2.GetBody().GetUserData()]:
            return
        for listener in self.listeners:
            if self.testListener(listener): continue
            listener.Add(point)

    def Persist(self, point):
        if None in [point.shape1.GetBody().GetUserData(),
                    point.shape2.GetBody().GetUserData()]:
            return
        for listener in self.listeners:
            if self.testListener(listener): continue
            listener.Persist(point)

    def Remove(self, point):
        if None in [point.shape1.GetBody().GetUserData(),
                    point.shape2.GetBody().GetUserData()]:
            return
        for listener in self.listeners:
            if self.testListener(listener): continue
            listener.Remove(point)"""

    def testListener(self, listener):
        if not listener.isAlive():
            self.removeListener(listener)
            return True
        else:
            return False
        
    def addListener(self, listener):
        self.listeners.append(listener)

    def removeListener(self, listener):
        self.listeners.remove(listener)
        del listener

    def clearListeners(self):
        self.listeners = []

class BaseListener(box2d.b2ContactListener):
    alive = True

    def __init__(self):
        super(BaseListener, self).__init__()
        self.alive = True
        
    def isAlive(self):
        return self.alive

    def destroy(self):
        self.alive = False
