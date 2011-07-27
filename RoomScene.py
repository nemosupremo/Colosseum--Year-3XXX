import Scene
import UI
import util
import pygame
import os
import GameClient

class RoomScene(Scene.Scene):

    roomName = "0007 : Custom Room Name"
    roomFont = None
    roomF_Rendered = None
    handles = [GameClient.CALL_PLAYERLIST,
               GameClient.CALL_NEWPLAYER,
               GameClient.CALL_PLAYERLEFT,
               GameClient.CALL_CHAT,
               GameClient.CALL_ROOMSTAT,
               GameClient.CALL_LEAVEROOM]

    chatData = []

    def createHandleFunctions(self):
        self.handleFunc = {
            GameClient.CALL_PLAYERLIST : self.updatePlayers,
               GameClient.CALL_NEWPLAYER : self.updatePlayers,
               GameClient.CALL_PLAYERLEFT : self.updatePlayers,
               GameClient.CALL_CHAT : self.doChat,
               GameClient.CALL_ROOMSTAT : self.roomStat,
               GameClient.CALL_LEAVEROOM : self.kicked
        }

    def getRoomName(self, roomId, roomName):
        return "%.4d : %s" % (roomId, roomName)

    def doChat(self, data):
        self.chatData.append(data)
        if len(self.chatData) > 29:
            self.chatData = self.chatData[-29:]
        self.chatList.setItems(self.chatData)

    def roomStat(self, data):
        if data[0] == self.MAIN.client.stateDict["PLAYING"]:
            self.MAIN.startGame()
        
    def kicked(self):
        pass

    def onStart(self):
        self.MAIN.client.startGame()

    def onLeave(self):
        self.MAIN.client.leaveRoom()

    def onTextEnter(self):
        txt = self.chatTxt.getText()
        self.chatTxt.setText("")
        self.MAIN.client.sendChat(txt)
        
    def setUp(self):
        self.chatData = []
        util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'chat_back.png')]
        util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'users_back.png')]

        fontFile = os.path.join(util.IMAGES['HUD'], "def.ttf")
        self.roomFont = pygame.font.Font(fontFile, 30)
        self.roomF_Rendered = self.roomFont.render(self.getRoomName(self.MAIN.client.roomId, self.MAIN.client.roomName), False, (0, 0, 0))
        
        self.userList = UI.List(768,768-46, None, 20,768,45)

        self.chatList = UI.List(766,464, None, 20, 0, 45+490+2-232)
        self.chatList.selectable(False)
        self.chatTxt = UI.TextInput(766, None, 20, 0, 768-19)
        self.chatTxt.setEnterFunc(self.onTextEnter)
        self.startButton = UI.Button(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'start.png')],
                                    util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'start_over.png')],
                                    477, 5)
        self.startButton.setOnClick(self.onStart)
        self.leaveButton = UI.Button(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'leave.png')],
                                    util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'leave_over.png')],
                                    627, 5)
        self.leaveButton.setOnClick(self.onLeave)
        
        self.MAIN.eventManager.addHandler(self.startButton)
        self.MAIN.eventManager.addHandler(self.leaveButton)
        self.MAIN.eventManager.addHandler(self.userList)
        self.MAIN.eventManager.addHandler(self.chatList)
        self.MAIN.eventManager.addHandler(self.chatTxt)
        

        self.MAIN.cam.addOverlay(self)
        self.MAIN.cam.addOverlay(self.startButton)
        self.MAIN.cam.addOverlay(self.leaveButton)
        self.MAIN.cam.addOverlay(self.userList)
        self.MAIN.cam.addOverlay(self.chatList)
        self.MAIN.cam.addOverlay(self.chatTxt)

        self.updatePlayers()
        super(RoomScene, self).setUp()

    def setRoomName(self,roomName):
        self.roomName = roomName
        self.roomF_Rendered = self.roomFont.render(self.roomName, False, (0, 0, 0))

    def updatePlayers(self, *args):
        pls = self.MAIN.client.getPlayers()
        playerList = []
        for player in pls:
            playerList.append("%s%s%s" % (player[5], " [Master]" if player[4] else "", " [Winner]" if player[0] == self.MAIN.client.winnerId else ""))
        self.userList.setItems(playerList)

    def destroy(self):
        self.MAIN.eventManager.removeHandler(self.startButton)
        self.MAIN.eventManager.removeHandler(self.leaveButton)
        self.MAIN.eventManager.removeHandler(self.userList)
        self.MAIN.eventManager.removeHandler(self.chatList)
        self.MAIN.eventManager.removeHandler(self.chatTxt)
        

        self.MAIN.cam.removeOverlay(self)
        self.MAIN.cam.removeOverlay(self.startButton)
        self.MAIN.cam.removeOverlay(self.leaveButton)
        self.MAIN.cam.removeOverlay(self.userList)
        self.MAIN.cam.removeOverlay(self.chatList)
        self.MAIN.cam.removeOverlay(self.chatTxt)

        del self.startButton
        del self.leaveButton
        del self.userList
        del self.chatList
        del self.chatTxt
        
        util.IMAGECACHE.clear()
        super(RoomScene, self).destroy()

    def draw(self, surface, offset=(0,0)):
        surface.blit(self.roomF_Rendered, (10,45))
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'users_back.png')], (788,219))
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'chat_back.png')], (250,624-(232/2)))

    def canChangeChar(self):
        return True
