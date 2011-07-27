import pygame
import os
from util import box2d # This is done with all files to prevent a bug
from threading import Thread
from random import randint
from time import sleep, time

import util
import Camera
import EventMan
import EscMenu
import ChangeChar

from TitleScene import TitleScene
from LobbyScene import LobbyScene
from RoomScene import RoomScene
from GameScene import GameScene

import GameClient
import Network

class main(object):

    screen = None
    running = False
    clock = None
    world = None
    cam = None
    eventManager = None
    mainChar = None
    stage = None
    client = None
    fps_font = None
    debug_font = None
    hud = None
    escapeMenu = None
    changeMenu = None

    otherPlayers = []
    status = 0
    currentScene = []
    charId = 3

    controller = None

    pickups = []
    pickupsRendered = True
    

    def __init__(self):
        util.seedRandom()
        """ PYGAME """
        pygame.display.init()
        pygame.font.init()
        pygame.mixer.init(22050,-16,2,2**20)

        self.fps_font = pygame.font.Font(None, 24)
        self.debug_font = pygame.font.Font(None, 15)
        self.screen = pygame.display.set_mode((util.CANVAS_WIDTH, util.CANVAS_HEIGHT), util.DISPLAY_FLAGS)
        self.cam = Camera.Camera(self.screen)
        util.IMAGECACHE.setLoadFunc(util.loadImage)
        util.SOUNDCACHE.setLoadFunc(util.loadSound)

        """ WORLD """
        self.clock = pygame.time.Clock()

        """ EVENT MANAGER """
        self.eventManager = EventMan.EventMan(pygame.event)
        self.eventManager.addHandler(self)

    """ EVENT FUNCTIONS """
    def processEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.endProgram()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.escapeMenu == None:
                        if self.changeMenu == None:
                            self.escMenu()
                    else:
                        self.escMenuClick(0)

    def escMenu(self):
        self.escapeMenu = EscMenu.EscMenu()
        self.escapeMenu.canChangeChar(self.activeScene.canChangeChar())
        self.escapeMenu.canLeaveGame(self.activeScene.canLeaveGame())
        self.escapeMenu.setHandler(self.escMenuClick)
        self.cam.addOverlay(self.escapeMenu)
        self.eventManager.addHandler(self.escapeMenu)

    def escMenuClick(self, action):
        if action == self.escapeMenu.CLICK_QUIT:
            self.endProgram()
        elif action == self.escapeMenu.CLICK_CHANGE:
            self.changeChar()
        elif action == self.escapeMenu.CLICK_LEAVE:
            self.client.leaveRoom()
        self.cam.removeOverlay(self.escapeMenu)
        self.eventManager.removeHandler(self.escapeMenu)
        self.escapeMenu = None

    def changeChar(self):
        self.changeMenu = ChangeChar.ChangeChar(self.client.charId)
        self.changeMenu.setHandler(self.changeClick)
        self.cam.addOverlay(self.changeMenu)
        self.eventManager.addHandler(self.changeMenu)

    def changeClick(self, newCharId):
        self.cam.removeOverlay(self.changeMenu)
        self.eventManager.removeHandler(self.changeMenu)
        self.changeMenu = None
        if newCharId != None:
            self.client.setCharacter(newCharId)

    def changeScene(self, NewScene):
        if self.escapeMenu != None:
            self.escMenuClick(0)
        if self.changeMenu != None:
            self.changeClick(None)
        self.cam.stopDrawing()
        self.activeScene.destroy()
        self.activeScene = NewScene(self)
        self.activeScene.setUp()
        self.cam.continueDrawing()

    def startGame(self):
        self.changeScene(GameScene)

    def endGame(self):
        self.changeScene(RoomScene)


    """ ONLINE/NETWORKING FUNCTIONS """
    def onConnect(self, result):
        if result:
            self.changeScene(LobbyScene)
        else:
            self.activeScene.setLoading(False)
            self.activeScene.connectVisible(True)
            self.activeScene.setErrorMessage("Error: Failed to connect to server.")
        
    def onDisconnect(self):
        self.changeScene(TitleScene)
        self.activeScene.setLoading(False)
        self.activeScene.connectVisible(True)
        self.activeScene.setErrorMessage("Error: Disconnected.")
        "GO TO HOME SCREEN"

    def onRoomSwitch(self, action, result):
        if result:
            if action == self.client.LEAVING_ROOM:
                self.changeScene(LobbyScene)
            else:
                if self.client.roomState == self.client.stateDict['PLAYING']:
                    self.changeScene(GameScene)
                else:
                    self.changeScene(RoomScene)
        else:
            if type(self.activeScene) == LobbyScene:
                self.activeScene.createPop = None
            if action == self.client.JOINING_ROOM:
                self.activeScene.doChat(("Failed to join room.", (255,0,0)))
            elif action == self.client.LEAVING_ROOM:
                self.activeScene.doChat(("Failed to leave room.", (255,0,0)))

    def handleNetworkCall(self, call, args):
        if self.activeScene != None and self.activeScene.handlesCall(call):
            self.activeScene.handleCall(call, args)
    
    """ MAIN FUNCTION """

    def main(self):
        self.activeScene = TitleScene(self)
        self.activeScene.setUp()
        self.mainLoop()

    def mainLoop(self):
        self.running = True
        while self.running:
            self.clock.tick(util.FRAMERATE)
            self.eventManager.processEvents()

            if self.activeScene != None:
                self.activeScene.mainLoop()
            
            self.cam.render()
            fps = self.fps_font.render("%f" % self.clock.get_fps(), 1, (10, 10, 10))
            self.screen.blit(fps, (0,0))
            pygame.display.flip()     

    def endProgram(self):
        if self.client:
            self.client.disconnect()
        self.activeScene.destroy()
        self.activeScene = None
        
        self.running = False
    """ FLOW CONTROL """

    def connect(self, name, server):
        self.client = GameClient.GameClient(self)
        if server.find(":") > 0:
            server = server[:server.find(":")]
            port = int(server[server.find(":")+1:])
        else:
            port = 62227
        self.client.connect_async(name, (server, port))
        self.activeScene.connectVisible(False)
        self.activeScene.setLoading(True)
        
    """
    def control(self):
        self.client = GameClient.GameClient(self)
        name = raw_input("Name: ")
        if not self.client.connect(name, ("localhost", 62227)):
            print "Connection failed"
            self.running = False
            return
        while True:
            cmd = raw_input(">>>")
            if cmd == "players":
                print self.client.getPlayers()
            elif cmd == "rooms":
                print self.client.getRooms()
            elif cmd[:4] == "join":
                print "Joining room..."
                rid = int(cmd[5:])
                if self.client.joinRoom(rid):
                    print "joined room"
                else:
                    print "failed to join room"
            elif cmd[:4] == "make":
                name = cmd[5:]
                self.client.makeRoom(name)
            elif cmd[:6] == "change":
                self.charId = int(cmd[7:])
                self.client.setCharacter(self.charId)
            elif cmd == "leave":
                self.client.leaveRoom()
            elif cmd == "quit":
                self.client.disconnect()
                self.running = False
                break
            elif cmd == "start":
                self.client.startGame()

    """        

if __name__ == "__main__":
    game = main()
    game.main()
