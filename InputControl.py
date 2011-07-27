import util
import EventMan
import pygame

class InputControl(EventMan.EventHandle):

    eventFuncs = {}
    
    def __init__(self):
        self.eventFuncs[pygame.MOUSEMOTION] = self.MouseMove
        self.eventFuncs[pygame.MOUSEBUTTONDOWN] = self.MouseDown
        self.eventFuncs[pygame.MOUSEBUTTONUP] = self.MouseUp
        self.eventFuncs[pygame.KEYDOWN] = self.KeyDown
        self.eventFuncs[pygame.KEYUP] = self.KeyUp
        
    def processEvents(self, events):
        for event in events:
            if event.type in self.eventFuncs.keys():
                self.eventFuncs[event.type](event)

    def MouseMove(self, event):
        pass

    def MouseDown(self, event):
        pass

    def MouseUp(self, event):
        pass

    def KeyDown(self, event):
        pass

    def KeyUp(self, event):
        pass

    def addEvent(self, eventType, func):
        self.eventFuncs[eventType] = func

    def removeEvent(self, eventType):
        del self.eventFuncs[eventType]

    def getEvents(self):
        return self.eventFuncs.keys()
