class Scene(object):

    MAIN = None
    setup = False
    destroyed = False
    handles = []
    handleFunc = {}

    def __init__(self, MainObj):
        self.MAIN = MainObj
        self.createHandleFunctions()

    def createHandleFunctions(self):
        pass
    
    def setUp(self):
        self.setup = True

    def mainLoop(self):
        pass

    def destroy(self):
        self.destroyed = True

    def isSetUp(self):
        return self.setup

    def isDestroyed(self):
        return self.destroyed

    def handlesCall(self, call):
        return call in self.handles

    def handleCall(self, call, args):
        return self.handleFunc[call](*args)

    def canChangeChar(self):
        return False

    def canLeaveGame(self):
        return False
