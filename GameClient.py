import Network
from time import sleep
from threading import Thread

CALL_ROOMLIST = 0
CALL_WEAPLIST = 1
CALL_PLAYERLIST = 2
CALL_NEWPLAYER = 3
CALL_PLAYERLEFT = 4
CALL_CHAT = 5
CALL_PLAYERDAT = 6
CALL_ROOMSTAT = 7
CALL_LEAVEROOM = 8
CALL_SHOOT = 9
CALL_SCORE = 10

class GameClient(Network.Client):
    CONNECTING = 0
    JOINING_ROOM = 1
    LEAVING_ROOM = 2
    rooms = []
    players = []
    weapList= []
    scores = {}
    response = {}
    currRoomInfo = None
    main = None
    status = -1
    charId = 0
    roomState = -1
    roomId = 0
    roomName = ""
    stateDict = {
       "WAITING":0,
       "PLAYING":1,
       "DEAD":99
    }
    invStateDict = {
        0:"WAITING",
       1:"PLAYING",
       99:"DEAD"
    }
    
    winnerId = -1

    def __init__(self, main):
        super(GameClient, self).__init__()
        self.main = main
        self.rooms = []
        self.scores = {}
        self.players =[]
        self.weapList = []
        self.response = {}

    def connect(self, name, addr, evt=False): #Blocks
        self.status = self.CONNECTING
        super(GameClient, self).connect(name, addr)
        if evt:
            self.onConnect(self.complete(self.CONNECTING))
        else:
            return self.complete(self.CONNECTING)

    def connect_async(self, name, addr): #Doesn't block
        t = Thread(target=self.connect, args=[name, addr, True])
        t.start()

    # NETWORK FUNCTIONS
    def complete(self, event, timeout = 2):
        waited = 0
        while event == self.status and waited <= timeout:
            sleep(.1)
            waited += .1
        if waited >= timeout:
            return False
        return self.response[event]

    def done(self, event, response):
        self.response[event] = response
        self.status = -1

    def playerById(self, pId):
        low = 0
        high = len(self.players) - 1
        while low <= high:
            mid = (low + high) >> 1
            midId = self.players[mid][0]

            if midId < pId:
                low = mid + 1
            elif midId > pId:
                high = mid - 1
            else:
                return mid
        return None

    def getPlayers(self):
        return self.players

    def getRooms(self):
        return self.rooms        

    def clearScores(self):
        self.scores = {}

    # EVENT FUNCTIONS

    def onConnect(self, result):
        self.main.onConnect(result)
    
    def onRoomList(self, data):
        self.rooms = data
        self.main.handleNetworkCall(CALL_ROOMLIST, (self.rooms,))

    def onWeapList(self, data):
        self.weapList = data
        self.main.handleNetworkCall(CALL_WEAPLIST, (self.weapList,))

    def onPlayerList(self, playerList, roomId, roomState, yourId):
        self.players = playerList
        self.playerId = yourId
        self.players.sort()
        self.roomId = roomId
        self.roomState = roomState
        if self.status in [self.CONNECTING, self.JOINING_ROOM, self.LEAVING_ROOM]:
            self.done(self.status, True)
        self.main.handleNetworkCall(CALL_PLAYERLIST, (self.players,))
            

    def onNewPlayer(self, player):
        #playername = player[0][:player[0].find('\00')]
        self.players.append(player)
        self.players.sort()
        self.main.handleNetworkCall(CALL_NEWPLAYER, (player,))

    def onPlayerLeft(self, data):
        playerPos = self.playerById(data[0])
        player = self.players[playerPos]
        del self.players[playerPos]
        if data[2] != -1:
            self.players[self.playerById(data[2])] = self.changeTuple(self.players[self.playerById(data[2])], 4, True)
        self.main.handleNetworkCall(CALL_PLAYERLEFT, (player,))

    def changeTuple(self, tup, key, value):
        flist = list(tup)
        flist[key] = value
        return tuple(flist)

    def onChat(self, data):
        self.main.handleNetworkCall(CALL_CHAT, (data,))

    def onPlayerData(self, data):
        self.main.handleNetworkCall(CALL_PLAYERDAT, (data,))

    def onRoomStat(self, data):
        self.winnerId = data[1]
        self.main.handleNetworkCall(CALL_ROOMSTAT, (data,))
        #if data[0] == 0:
        #    self.main.endGame()
        #elif data[0] == 1:
        #    print "starting game"
        #    self.main.startGame()

    def onRoomSwitch(self, action, result):
        self.main.onRoomSwitch(action, result)
        return result

    def onLeaveRoom(self):
        if self.status in [self.JOINING_ROOM]:
            self.done(self.status, False)

    def onShoot(self, bulletdata):
        self.main.handleNetworkCall(CALL_SHOOT, (bulletdata,))
    
    def onScore(self, score):
        self.scores[score[0]] = score[1], score[2]
        self.scores[score[3]] = score[4], score[5]
        self.main.handleNetworkCall(CALL_SCORE, (score,))

    def onChangeChar(self, charId, playerId):
        playerPos = self.playerById(playerId)
        player = self.players[playerPos]
        self.players[playerPos] = self.changeTuple(self.players[playerPos], 3, charId)

    def onDisconnect(self):
        self.main.onDisconnect()

    ## SENDING FUNCTIONS

    def joinRoom(self, roomid, roomName, block=False):
        if block:
            self.status = self.JOINING_ROOM
            self.sendDataReliable(Network.Structs.joinRoom.dataType, Network.Structs.joinRoom.pack(roomid)).join()
            # This function blocks...
            return self.onRoomSwitch(self.JOINING_ROOM, self.complete(self.JOINING_ROOM))
        else:
            self.winnerId = -1
            self.roomName = roomName
            Thread(target=self.joinRoom, args=[roomid, roomName, True]).start()

    def makeRoom(self, roomName, block=False):
        if block:
            self.status = self.JOINING_ROOM
            self.sendDataReliable(Network.Structs.makeRoom.dataType, Network.Structs.makeRoom.pack(len(roomName))+roomName)
            return self.onRoomSwitch(self.JOINING_ROOM, self.complete(self.JOINING_ROOM))
        else:
            self.winnerId = -1
            self.roomName = roomName
            Thread(target=self.makeRoom, args=[roomName, True]).start()

    def leaveRoom(self, block=False):
        if block:
            self.status = self.LEAVING_ROOM
            self.sendDataReliable(Network.Structs.leaveRoom.dataType, Network.Structs.leaveRoom.pack())
            return self.onRoomSwitch(self.LEAVING_ROOM, self.complete(self.LEAVING_ROOM))
        else:
            self.winnerId = -1
            Thread(target=self.leaveRoom, args=[True]).start()

    def startGame(self):
        self.sendDataReliable(Network.Structs.startGame.dataType, Network.Structs.startGame.pack(0))

    def sendGameData(self, gameData):
        self.sendData(Network.Structs.playerDat.dataType, gameData)

    def sendShoot(self, bullet):
        self.sendDataReliable(Network.Structs.shoot.dataType, Network.Structs.shoot.pack(-1, bullet.x, bullet.y, bullet.angle, bullet.type))

    def setCharacter(self, charId):
        self.sendDataReliable(Network.Structs.setCharacter.dataType, Network.Structs.setCharacter.pack(charId, 0))
        self.charId = charId

    def sendDeath(self, killerid):
        self.sendDataReliable(Network.Structs.onDeath.dataType, Network.Structs.onDeath.pack(killerid))

    def sendPicked(self, serverId):
        self.sendDataReliable(Network.Structs.takeWeap.dataType, Network.Structs.takeWeap.pack(serverId))

    def sendChat(self, data):
        self.sendDataReliable(Network.Structs.preChat.dataType, Network.Structs.preChat.pack(len(data)) + data)

    def __del__(self):
        super(GameClient, self).__del__()
