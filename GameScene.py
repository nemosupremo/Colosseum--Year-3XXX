import Scene
import World
import util
import Character
import hud
import Stage
import Controller
import pygame
import Network
import GameClient
import Pickup
from threading import Thread
from time import sleep

class GameScene(Scene.Scene):
    otherPlayers = []
    pickups = []
    pickupsRendered = False
    controller = None
    mainChar = None
    world = None
    network = False
    
    handles = [GameClient.CALL_WEAPLIST,
               GameClient.CALL_NEWPLAYER,
               GameClient.CALL_PLAYERLEFT,
               GameClient.CALL_PLAYERDAT,
               GameClient.CALL_ROOMSTAT,
               GameClient.CALL_LEAVEROOM,
               GameClient.CALL_SHOOT,
               GameClient.CALL_SCORE]

    def createHandleFunctions(self):
        self.handleFunc = {
            GameClient.CALL_WEAPLIST : self.updateWeaps,
            GameClient.CALL_NEWPLAYER : self.onNewPlayer,
            GameClient.CALL_PLAYERLEFT : self.onPlayerLeft,
            GameClient.CALL_PLAYERDAT : self.updateGame,
            GameClient.CALL_ROOMSTAT : self.roomStat,
            GameClient.CALL_LEAVEROOM : self.kicked,
            GameClient.CALL_SHOOT : self.onShoot,
            GameClient.CALL_SCORE : self.onScore,
        }

    def makeWorld(self):
        self.stage = Stage.Stage(self.world, util.XML['WORLD'])

    def getOtherPlayers(self):
        self.otherPlayers = []
        for player in self.MAIN.client.getPlayers():
            if player[0] != self.MAIN.client.playerId:
                char = Character.Character(self.world, False, player[3], 0, 1, None,None, True)
                char.setPlayerId(player[0])
                char.setPlayerName(player[5])
                self.otherPlayers.append(char)
                self.world.addActor(char)
        self.otherPlayers.sort(cmp=lambda x,y: x.getPlayerId() - y.getPlayerId())

    def getCharacter(self, playerId, index=False):
        low,high = 0,len(self.otherPlayers) - 1
        while low <= high:
            mid = (low + high) >> 1
            midId = self.otherPlayers[mid].getPlayerId()
            if midId < playerId: low = mid + 1
            elif midId > playerId: high = mid - 1
            else: return mid if index else self.otherPlayers[mid]
        return None

    def roomStat(self, data):
        if data[0] == self.MAIN.client.stateDict["WAITING"]:
            self.MAIN.endGame()

    def kicked(self, data):
        pass

    def updateGame(self, data):
        if self.mainChar == None:return
        for player in data:
            if player[0] == -1:continue
            char = self.getCharacter(player[0])
            if char == None:continue
            char.setManagedData(player[1], (player[2], player[3]), player[4], player[5], player[6], player[7], self.mainChar)
            
    def onShoot(self, bulletdata):
        if bulletdata[0] == -1: return
        char = self.getCharacter(bulletdata[0])
        if char == None: return
        char.ActionShoot(0,0,bulletdata)

    def onNewPlayer(self, player):
        char = Character.Character(self.world, False, player[3], 0, 1, 0,0, True)
        char.setPlayerId(player[0])
        char.setPlayerName(player[5])
        self.otherPlayers.append(char)
        self.world.addActor(char)
        self.otherPlayers.sort(cmp=lambda x,y: x.getPlayerId() - y.getPlayerId())
        self.hud.addText("%s has joined the game" % char.getPlayerName())

    def onPlayerLeft(self, player):
        char = self.getCharacter(player[0], True)
        if char == None: return
        if self.isSetUp():
            charObj = self.otherPlayers[char]
            charName = charObj.getPlayerName()
            del self.otherPlayers[char]
            charObj.destroy()
            self.hud.addText("%s has left the game." % charName)

    def onScore(self, score):
        oscore = 0,3
        if score[0] == self.MAIN.client.playerId:
            self.mainChar.kills, self.mainChar.deaths = score[1], score[2]
            oscore = (3,)
        elif score[3] == self.MAIN.client.playerId:
            self.mainChar.kills, self.mainChar.deaths = score[4], score[5]
            oscore = (0,)

        for oid in oscore:
            char = self.getCharacter(score[oid])
            if char == None: continue
            char.kills, char.deaths = score[oid+1], score[oid+2]

    def updateWeaps(self, weaps):
        for pickup in self.pickups:
            if type(pickup) != tuple:
                pickup.valid = False
        self.pickups = []
        self.pickupsRendered = False
        for weap in weaps:
            if weap[1] != -99:
                if self.isSetUp():
                    pu = Pickup.Pickup(self.world, weap[1], weap[0], weap[2],weap[3])
                    self.world.addActor(pu)
                else: pu = (None, weap[1], weap[0], weap[2],weap[3])
                self.pickups.append(pu)
        self.pickupsRendered = self.isSetUp()
    
    def setUp(self, onlineMode = True):
        #self.world = World.World(util.WORLDBOUNDS(), util.GRAVITY, True)
        self.world = World.World(util.GRAVITY, True)
        self.world.setCamera(self.MAIN.cam)
        if self.MAIN.client: self.world.setGameClient(self.MAIN.client)
        
        self.makeWorld()
        self.MAIN.cam.setStage(util.getFile(util.IMAGES, 'STAGE', self.stage.stageFile))

        xbound = ((self.stage.MINX+200), (self.stage.MAXX-200))
        ybound = ((self.stage.MINY+200), (self.stage.MAXY-200))
        
        self.mainChar = Character.Character(self.world, True, self.MAIN.client.charId, 1, 1, xbound, ybound)
        self.mainChar.name = "person"
        if self.MAIN.client:
            self.mainChar.setPlayerId(self.MAIN.client.playerId)
        self.hud = hud.hud()
        self.mainChar.linkHud(self.hud)
        self.controller = Controller.Controller(self.mainChar)
        self.world.setMainCharacter(self.mainChar)

        self.MAIN.cam.addOverlay(self.hud)
        self.world.addActor(self.mainChar)

        if False: #Set True, for debugging, dangerous
            self.MAIN.cam.addActor(self.stage.getSprites())
            
        self.MAIN.cam.setFocus(self.mainChar)
        self.MAIN.cam.setFocusPoint((util.CANVAS_WIDTH/2,util.CANVAS_HEIGHT/2))
        self.MAIN.cam.setBackground(util.getFile(util.IMAGES, 'BG', '1.jpg'),
                               self.stage.getWidth(), self.stage.getHeight())

        self.MAIN.eventManager.addHandler(self.controller)
        
        self.world.addContactListener( self.mainChar.getCharContact() )
        self.mainChar.spawn()
        if not self.pickupsRendered:
            np = []
            for pu in self.pickups:
                npu = (self.world,) + pu[1:]
                pus = Pickup.Pickup(*npu)
                self.world.addActor(pus)
                np.append(pus)
            self.pickups = np

        if not onlineMode:
            self.pu = Pickup.Pickup(self.world, 02, 0, 40.8616,2.16167)
            self.world.addActor(self.pu)

        if onlineMode:
            self.getOtherPlayers()
            self.network = True
            Thread(target=self.networkLoop).start()

        super(GameScene, self).setUp()

    def networkLoop(self):
        while self.network:
            if self.mainChar != None:
                self.MAIN.client.sendGameData(self.mainChar.buildNetworkData())
            sleep(Network.settings.GAME_INTERVAL)

    def mainLoop(self):
        if self.controller and self.world and self.mainChar:
            self.controller.MainLoop(pygame.key.get_pressed())
            self.world.Step()
            self.mainChar.mainLoop()

    def destroy(self):
        self.network = False
        self.stage.destroy()
        del self.stage
        self.stage = None

        self.MAIN.cam.setFocus(None)
        self.mainChar.destroy()
        del self.mainChar
        self.mainChar = None

        for player in self.otherPlayers:
            player.destroy()
        self.otherPlayers = []

        self.MAIN.cam.removeOverlay(self.hud)
        self.hud.destroy()

        self.MAIN.cam.setBackground(None,0,0)
        self.MAIN.cam.setStage(None)

        for pickup in self.pickups:
            pickup.destroy()

        self.world.destroy()
        self.world = None
        super(GameScene, self).destroy()

    def canLeaveGame(self):
        return True
