import util
import pygame

class EventHandle(object):
    
    def processEvents(self, events):
        pass

class EventMan(object):
    evntHandlers = []
    evntFunctions = []
    events = []
    event = None
    evntFunc = None

    def __init__(self, event):
        self.event = event

    def processEvents(self):
        self.events = self.event.get()
        #for func in self.evntFunctions:
        #    if self.event.peek(func[0]):
        #        func[1](*func[2])
        for handle in self.evntHandlers:
            handle.processEvents(self.events)

    def addFunction(self, event, function, args=[]):
        self.evntFunctions.append([event, function, args])

    def removeFunction(self, function):
        for f in xrange(len(self.evntFunctions)):
            if self.evntFunctions[f][1] == function:
                self.evntFunctions.remove(f)
                break

    def addHandler(self, handler):
        self.evntHandlers.append(handler)

    def removeHandler(self, handler):
        self.evntHandlers.remove(handler)

    def removeAllEvents(self):
        self.evntHandlers.clear()
        self.evntFunctions.clear()
                
            
