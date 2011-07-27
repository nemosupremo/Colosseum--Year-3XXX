import util
import InputControl
import Character
import pygame

class Controller(InputControl.InputControl):

    KeyControls = {
        pygame.K_a : "LEFT",
        pygame.K_d : "RIGHT",
        pygame.K_w : "JUMP",
        pygame.K_r : "RELOAD",
        pygame.K_e : "PICKUP"
        #pygame.K_DOWN : "DOWN"
    }

    HOLDABLE = ["LEFT", "RIGHT"]
    SINGLE = ["JUMP", "RELOAD", "PICKUP"]

    KeyActions = None
    down = []

    char = None
    #spBody = None
    
    def __init__(self, char):
        super(Controller, self).__init__()
        self.char = char
        #self.spBody = self.sprite.getB2Body()
        self.setKeys()

    def setKeys(self):
        self.KeyActions = {
            "LEFT" : self.ActionLeft,
            "RIGHT" : self.ActionRight,
            "JUMP" : self.ActionJump,
            "RELOAD" : self.ActionReload,
            "PICKUP" : self.ActionPickup
            #"SHOOT" : self.ActionShoot
        }

    def ActionLeft(self):
        self.char.ActionRun(Character.Character.LEFT)

    def ActionRight(self):
        self.char.ActionRun(Character.Character.RIGHT)

    def ActionJump(self):
        self.char.ActionJump()

    def ActionReload(self):
        self.char.ActionReload()

    def ActionPickup(self):
        self.char.ActionPickup()

    def MouseDown(self, event):
        if event.button == 1:
            self.char.ActionShoot(event.pos[0], event.pos[1])
    
    def KeyDown(self, event):
        if event.key in self.KeyControls:
            if not self.KeyControls[event.key] in self.HOLDABLE:
                self.KeyActions[self.KeyControls[event.key]]()

    def MouseMove(self, event):
        self.char.ActionMouse(event.pos[0], event.pos[1])

    def MainLoop(self, keys):
        for key in self.KeyControls:
            if self.KeyControls[key] in self.SINGLE: continue
            if keys[key] and not key in self.down:
                self.KeyActions[self.KeyControls[key]]()
