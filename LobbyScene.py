import Scene
import UI
import util
import pygame
import GameClient
import CreateRoom

class LobbyScene(Scene.Scene):

    handles = [GameClient.CALL_ROOMLIST,
               GameClient.CALL_PLAYERLIST,
               GameClient.CALL_NEWPLAYER,
               GameClient.CALL_PLAYERLEFT,
               GameClient.CALL_CHAT,
               GameClient.CALL_LEAVEROOM]

    def createHandleFunctions(self):
        self.handleFunc = {
            GameClient.CALL_ROOMLIST : self.updateRooms,
            GameClient.CALL_PLAYERLIST : self.updatePlayers,
            GameClient.CALL_NEWPLAYER : self.updatePlayers,
            GameClient.CALL_PLAYERLEFT : self.updatePlayers,
            GameClient.CALL_CHAT : self.doChat,
            GameClient.CALL_LEAVEROOM : self.failRoom
        }

    chatData = []

    createPop = None

    def updateRooms(self, *args):
        rms = self.MAIN.client.getRooms()
        roomList = []
        for room in rms:
            roomList.append(("%s - [%d/%d] - [%s]" % (room[6], room[1], room[2], self.MAIN.client.invStateDict[room[3]]), (0,0,0), room[0], room[6]))
        self.roomList.setItems(roomList)

    def updatePlayers(self, *args):
        pls = self.MAIN.client.getPlayers()
        playerList = []
        for player in pls:
            playerList.append(player[5])
        self.userList.setItems(playerList)

    def doChat(self, data):
        self.chatData.append(data)
        if len(self.chatData) > 14:
            self.chatData = self.chatData[-14:]
        self.chatList.setItems(self.chatData)

    def failRoom(self, data):
        self.doChat(("Failed to join room.", (255,0,0)))

    def onTextEnter(self):
        txt = self.chatTxt.getText()
        self.chatTxt.setText("")
        self.MAIN.client.sendChat(txt)

    def createClick(self, roomName = None):
        if roomName == None:
            if self.createPop == None:
                self.createPop = CreateRoom.CreateRoom()
                self.MAIN.cam.addOverlay(self.createPop)
                self.MAIN.eventManager.addHandler(self.createPop)            
                self.createPop.setHandler(self.createClick)
        else:
            self.MAIN.cam.removeOverlay(self.createPop)
            self.MAIN.eventManager.removeHandler(self.createPop)            
            if len(roomName) == 0:
                self.doChat(("Room name cannot be empty", (255,0,0)))
                self.createPop = None
            else:
                self.MAIN.client.makeRoom(roomName)
                self.createPop = 1
                
    
    def joinClick(self):
        if self.createPop == None and self.roomList.selected != None:
            roomId = self.roomList.getItems()[self.roomList.selected][2]
            roomName = self.roomList.getItems()[self.roomList.selected][3]
            self.MAIN.client.joinRoom(roomId, roomName)
            self.createPop = 1
        
    def setUp(self):
        self.chatData = []
        util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'title.png')]
        util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'chat_back.png')]
        util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'users_back.png')]
        util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'rooms_back.png')]
        
        self.roomList = UI.List(766,490, None, 20,0,45)
        
        self.userList = UI.List(768,768-46, None, 20,768,45)

        self.chatList = UI.List(766,232, None, 20, 0, 45+490+2)
        self.chatList.selectable(False)
        self.chatTxt = UI.TextInput(766, None, 20, 0, 768-19)
        self.chatTxt.setEnterFunc(self.onTextEnter)
        self.createButton = UI.Button(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'create.png')],
                                    util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'create_over.png')],
                                    477, 5)
        self.createButton.setOnClick(self.createClick)
        self.joinButton = UI.Button(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'join.png')],
                                    util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'join_over.png')],
                                    627, 5)
        self.joinButton.setOnClick(self.joinClick)
        self.MAIN.eventManager.addHandler(self.joinButton)
        self.MAIN.eventManager.addHandler(self.createButton)
        self.MAIN.eventManager.addHandler(self.roomList)
        self.MAIN.eventManager.addHandler(self.userList)
        self.MAIN.eventManager.addHandler(self.chatList)
        self.MAIN.eventManager.addHandler(self.chatTxt)
        

        self.MAIN.cam.addOverlay(self)
        self.MAIN.cam.addOverlay(self.joinButton)
        self.MAIN.cam.addOverlay(self.createButton)
        self.MAIN.cam.addOverlay(self.roomList)
        self.MAIN.cam.addOverlay(self.userList)
        self.MAIN.cam.addOverlay(self.chatList)
        self.MAIN.cam.addOverlay(self.chatTxt)

        self.updateRooms()
        self.updatePlayers()
        
        """
        self.MAIN.cam.addOverlay(self.chatTxt)
        self.MAIN.cam.addOverlay(self.createButton)
        self.MAIN.cam.addOverlay(self.joinButton)
        self.MAIN.cam.addOverlay(self)
        """
        super(LobbyScene, self).setUp()

    def setRooms(self,listrooms):
        self.roomList.setItems(listrooms)

    def setUsers(self,listusers):
        self.userList.setItems(listusers)

    def destroy(self):
        self.MAIN.eventManager.removeHandler(self.joinButton)
        self.MAIN.eventManager.removeHandler(self.createButton)
        self.MAIN.eventManager.removeHandler(self.roomList)
        self.MAIN.eventManager.removeHandler(self.userList)
        self.MAIN.eventManager.removeHandler(self.chatList)
        self.MAIN.eventManager.removeHandler(self.chatTxt)
        

        self.MAIN.cam.removeOverlay(self)
        self.MAIN.cam.removeOverlay(self.joinButton)
        self.MAIN.cam.removeOverlay(self.createButton)
        self.MAIN.cam.removeOverlay(self.roomList)
        self.MAIN.cam.removeOverlay(self.userList)
        self.MAIN.cam.removeOverlay(self.chatList)
        self.MAIN.cam.removeOverlay(self.chatTxt)

        del self.joinButton
        del self.createButton
        del self.roomList
        del self.userList
        del self.chatList
        del self.chatTxt
        
        util.IMAGECACHE.clear()
        super(LobbyScene, self).destroy()

    def draw(self, surface, offset=(0,0)):
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'title.png')], (0,0))
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'users_back.png')], (788,219))
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'chat_back.png')], (250,624))
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "LOBBY", 'rooms_back.png')], (219,252))

    def canChangeChar(self):
        return True
