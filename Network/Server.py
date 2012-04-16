import settings
import time
import Structs
import socket
import struct
from select import select
from time import sleep, time
from threading import Thread
import os
import random
import sys
import bisect

class Player(object):
    addr = None
    name = "Player"
    roomId = -1
    id = -1
    playerNo = 0
    server = None
    gameData = ""
    nRid = 0
    unrecievedMsg = []
    charId = 0

    kills = 0
    deaths = 0

    weaponId = 1
    isMaster = False
    isWinner = False
    connected = True

    lastTime = 0
    
    def __init__(self, server, id, addr, name):
        self.id = id
        self.name = name
        self.addr = addr
        self.server = server
        self.unrecievedMsg = []
        self.lastTime = time()

    def getAddrLong(self, ip):
        return struct.unpack('=L',socket.inet_aton(ip))[0]

    def resetGameData(self):
        self.gameData = Structs.playerDat.pack(-1,0,0,0,0,0,0,0)
        self.kills = 0
        self.deaths = 0
        self.isWinner = False

    def getAddrLongTuple(self):
        return (self.getAddrLong(self.addr[0]), self.addr[1])

    def getName(self):
        return self.name

    def getId(self):
        return self.id

    def getRoomPlayerList(self, exclude):
        if self.roomId == -1:
            return self.server.getPlayersInLobby(exclude)
        else:
            return self.server.getRoom(self.roomId).getPlayers(exclude)

    def getNextReliableId(self):
        self.nRid += 1
        if self.nRid >= 65536:
            self.nRid = 1
        return self.nRid

    def packInfo(self, playerInfo=True):
        #if playerInfo:
        return Structs.playerInfo.pack(self.id, self.playerNo, len(self.name), self.charId, self.isMaster) + self.name
        #else:
        #   return Structs.addPlayer.pack(self.name, self.id, self.playerNo, self.charId, 0)
        ##TYPE PLAYER INFO/DISCON

    def setCharId(self, charId):
        self.charId = charId
        if self.roomId != -1:
            playerList = self.getRoomPlayerList(self)
            for player in playerList:
                player.sendChangeChar(charId, self.getId())
      
    def sendPlayerList(self, playerList, roomId, roomState):
        playerInfo = ""
        for player in playerList:
            playerInfo += player.packInfo()
        data = [
                Structs.prePlayerList.pack(len(playerInfo), roomId, roomState, self.id),
                playerInfo
            ]
        self.sendDataReliable(Structs.prePlayerList.dataType, ''.join(data))

    def sendNewPlayer(self, player):
        self.sendDataReliable(Structs.newPlayer.dataType, player.packInfo())

    def sendRoomList(self, roomList):
        roomInfo = ""
        for room in roomList:
            roomInfo += room.packInfo()
        data = [
                Structs.preRoomList.pack(len(roomInfo)),
                roomInfo
            ]
        self.sendDataReliable(Structs.preRoomList.dataType, ''.join(data))

    def sendChatMsg(self, chatMsg):
        playerList = self.getRoomPlayerList(None)
        chatMsg = self.name +": "+ chatMsg
        for player in playerList:
            player.sendDataReliable(Structs.preChat.dataType, Structs.preChat.pack(len(chatMsg))+chatMsg)
            #self.server.sendData(data,player.addr)

    def sendChangeChar(self, charId, playerId):
        self.sendDataReliable(Structs.setCharacter.dataType, Structs.setCharacter.pack(charId,playerId))

    def sendGameStat(self, status, winnerId=-1):
        self.sendDataReliable(Structs.updateRoomStat.dataType, Structs.updateRoomStat.pack(status,winnerId))

    def sendPlayerLeft(self, player, new_ms_id=-1):
        self.sendDataReliable(Structs.playerLeft.dataType, Structs.playerLeft.pack(player.getId(), len(player.getName()), new_ms_id) + player.getName())


    def sendShoot(self, bullet, playerList):
        bullet = (self.id,) + bullet[1:]
        for player in playerList:
            player.sendDataReliable(Structs.shoot.dataType, Structs.shoot.pack(*bullet))
        
    def sendData(self, data):
        self.server.sendData(data,self.addr)

    def sendDataReliableThread(self, rid, data):
        for i in xrange(settings.MAX_TRIES):
            self.sendData(data)
            sleep(settings.SEND_WAIT)
            if not rid in self.unrecievedMsg:
                return
        self.server.disconnectPlayer(self)
            
    def sendDataReliable(self, dataType, data):
        rid = self.getNextReliableId()
        preDat = Structs.dataType.pack(dataType, rid)
        data = preDat + data
        self.unrecievedMsg.append(rid)
        t = Thread(target = self.sendDataReliableThread, args=[rid, data])
        t.start()
        return t

    def getRoomId(self):
        return self.roomId

    def setRoomId(self, roomId):
        self.roomId = roomId

    def setGameData(self, data):
        gd = Structs.playerDat.unpack(data)
        gd = (self.id,) + gd[1:]
        self.gameData = Structs.playerDat.pack(*gd)

    def getGameData(self):
        return self.gameData

    def setPlayerNo(self, playerNo):
        self.playerNo = playerNo

    def getPlayerNo(self):
        return self.playerNo

    def setGotData(self, rid):
        try:
            self.unrecievedMsg.remove(rid)
        except:
            pass # Data was really recieved
        
    def __cmp__(self, other):
        md = self.getAddrLongTuple()

        if type(other) == tuple or type(other) == list:
            od = self.getAddrLong(other[0]),other[1]
        elif type(other) == Player:
            od = other.getAddrLongTuple()
        else:
            return 0
            
        rs = md[0] - od[0]
        return rs if rs != 0 else (md[1] - od[1])

    def __eq__(self, other):
        
        if type(other) == tuple or type(other) == list:
            od = self.getAddrLong(other[0]),other[1]
        elif type(other) == Player:
            od = other.getAddrLongTuple()
        else:
            return False
            
        return self.getAddrLongTuple() == od

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        md = self.getAddrLongTuple()
        
        if type(other) == tuple or type(other) == list:
            od = self.getAddrLong(other[0]),other[1]
        elif type(other) == Player:
            od = other.getAddrLongTuple()
        else:
            return False

        if md[0] == od[0]:
            return md[1] < od[1]
        else:
            return md[0] < od[0]
        
    def __gt__(self, other):
        md = self.getAddrLongTuple()
        if type(other) == tuple or type(other) == list:
            od = self.getAddrLong(other[0]),other[1]
        elif type(other) == Player:
            od = other.getAddrLongTuple()
        else:
            return False
        
        if md[0] == od[0]:
            return md[1] > od[1]
        else:
            return md[0] > od[0]
        

class Room(object):
    players = []
    state = "WAITING"
    name = ""
    id = -1
    lastUpdate = 0
    stateDict = {
        "WAITING" : 0,
        "PLAYING" : 1,
        "DEAD" : 99
    }
    server = None
    gameThread = None
    game_kills = 25
    weaponSpawnTime = (30,60)
    WEAPON_IDS = [0,1,2,3,5,6,8,9,11,12,14,20,22,23,30,34,42,64,65,76,-1] #-1 = Health Pack
    WEAPON_LOCS = [
        (40.8616,2.16167), (115.175,2.16167), (83.7613,11.6283),
        (106.429,13.8950), (7.31099,15.0283), (22.7359,22.2635),
        (32.4962,22.2635), (59.4628,22.2635), (107.747,29.8659),
        (88.9124,36.2617), (78.5479,36.5634), (2.95513,36.9283)
        ]
    activeWeapons = [False]*12
    weapId = 0
    firstWeapSend = True
    gameKills = 15

    def __init__(self, server, name, rid):
        self.server = server
        self.name = name
        self.id = rid
        self.players = []
        self.activeWeapons = [False]*12
        

    def getPlayers(self, exclude = None):
        if exclude:
            r = []
            for player in self.players:
                if player != exclude: r.append(player)
            return r
        else:
            return self.players
    
    def assignPlayers(self):
        #self.players.sort(cmp=lambda x,y: x.getPlayerNo() - y.getPlayerNo())
        pNo = 1
        for player in self.players:
            player.setPlayerNo(pNo)
            pNo += 1

    def getId(self):
        return self.id

    def packInfo(self):
        return Structs.roomInfo.pack(self.id, len(self.players), settings.MAX_PLAYERS, self.stateDict[self.state], len(self.name), 0) + self.name
        
    def changeName(self, name):
        self.name = name
        for player in self.players:
            player.sendRoomName(self.name)

    def join(self, new_player):
        if len(self.players) >= settings.MAX_PLAYERS:
            return False
        new_player.isMaster = len(self.players) == 0

            
        self.players.append(new_player)
        new_player.setRoomId(self.getId())
        self.assignPlayers()
        
        for player in self.players:
            if player == new_player: continue
            player.sendNewPlayer(new_player)

        new_player.sendPlayerList(self.players, self.getId(), self.stateDict[self.state])

        return True


    def leave(self, player, disconnected=False):
        self.players.remove(player)
        player.setRoomId(-1)
        self.assignPlayers()
        if len(self.players) == 0:
            self.server.removeRoom(self)
        else:
            new_ms_id = -1
            player.isWinner = False
            if player.isMaster:
                self.players[0].isMaster = True
                player.isMaster = False
                new_ms_id = self.players[0].getId()
            for roomPlayer in self.players:
                roomPlayer.sendPlayerLeft(player, new_ms_id)

        if disconnected: self.server.removePlayer(player)
        return True

    def updatePlayer(self, player, data):
        player.setGameData(data)

    #def getScores(self):
    #    r = []
    #    for player in self.players:
    #        r.append([player.getName(), player.getKills(), player.getDeaths()])
    #    return r

    def manageDeath(self, deadplayer, killerid):
        killer = None
        for player in self.players:
            if player.getId() == killerid:
                killer = player

        killer.kills += 1
        deadplayer.deaths += 1

        data = Structs.sendScore.pack(killer.getId(), killer.kills, killer.deaths, deadplayer.getId(), deadplayer.kills, deadplayer.deaths)
        for player in self.players:
            player.sendDataReliable(Structs.sendScore.dataType, data)
        if killer.kills >= self.gameKills:
            self.state = "WAITING"
            killer.isWinner = True
            for player in self.players:
                player.sendGameStat(self.stateDict[self.state], killer.getId())

    def buildWeaponData(self):
        sz = Structs.preWeapon.pack(len(self.activeWeapons))
        weapInfos = []
        for weap in self.activeWeapons:
            if weap:
                weapInfos.append(Structs.weapon.pack(weap[0], weap[1], weap[2][0], weap[2][1]))
        return sz + ''.join(weapInfos)

    def spawnAllWeaps(self):
        self.activeWeapons = []
        for loc in self.WEAPON_LOCS:
            self.activeWeapons.append( [self.weapId, random.choice(self.WEAPON_IDS), loc, 0] )
            self.weapId += 1

    def sendWeapons(self):
        data = self.buildWeaponData()
        for player in self.players:
            player.sendDataReliable(Structs.preWeapon.dataType, data)

    def pickupWeap(self, svId):
        for weap in xrange(len(self.activeWeapons)):
            if self.activeWeapons[weap][0] == svId:
                self.activeWeapons[weap][1] = -99
                self.activeWeapons[weap][3] = time() + random.randint(*self.weaponSpawnTime)
                break

        self.sendWeapons()

    def checkWeapons(self):
        change = False
        for weap in xrange(len(self.activeWeapons)):
            if self.activeWeapons[weap][1] == -99:
                if time() > self.activeWeapons[weap][3]:
                    self.activeWeapons[weap][1] = random.choice(self.WEAPON_IDS)
                    self.activeWeapons[weap][3] = 0
                    change = True
        if change:
            self.sendWeapons()

    def startGame(self, player):
        if player.getPlayerNo() == 1 and self.state != "PLAYING":
            self.weapId = 0
            self.spawnAllWeaps()
            self.firstWeapSend = True
            self.state = "PLAYING"
            for player in self.players:
                player.resetGameData()
                player.sendGameStat(self.stateDict[self.state])
            self.gameThread = Thread(target = self.roomThread)
            self.gameThread.start()

    def roomThread(self):
        while self.state == "PLAYING" and self.server.running:
            self.update()
            sleep(settings.GAME_INTERVAL)

    def update(self):
        if self.state == "PLAYING":    
            playerDat = {}
            if self.firstWeapSend:
                self.sendWeapons()
                self.firstWeapSend = False
            for player in self.players:
                playerDat[player.getId()] = player.getGameData()

            for player in self.players:
                playerdata = ""
                for pd in playerDat:
                    if pd != player.getId(): playerdata += playerDat[pd]
                data = [
                    Structs.dataType.pack(Structs.prePlayerDat.dataType, 0),
                    Structs.prePlayerDat.pack(len(playerdata)),
                    playerdata
                ]
                toSend = ''.join(data)                    
                player.sendData(toSend)
            self.checkWeapons()
            

    def __del__(self):
        self.state = "DEAD"

class Server(object):
    rooms = []
    players = []
    sock = None
    buf = 2048
    running = False
    restart = False
    

    nextPlayerId = 0
    nextRoomId = 0

    onStTxt = """
--------------------------------
| Colosseum Year 3XXX
| Game Server
| Listening on %s:%d
--------------------------------

Commands :
-- players
---- Displays the number of connected players.
-- rooms
---- Displays the number of active rooms.
-- restart
---- Restarts the server
-- quit
---- Quits the server
"""

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.rooms = []
        self.players = []
        print self.onStTxt % (host,port)

    def getRoom(self, roomId):
        if roomId == -1: return self
        low = 0
        high = len(self.rooms) - 1
        while low <= high:
            mid = (low + high) >> 1
            midId = self.rooms[mid].getId()

            if midId < roomId:
                low = mid + 1
            elif midId > roomId:
                high = mid - 1
            else:
                return self.rooms[mid]
        return None

    def getPlayerByAddr(self, addr):
        low = 0
        high = len(self.players) - 1
        while low <= high:
            mid = (low + high) >> 1
            midPl = self.players[mid]

            if midPl < addr: low = mid + 1
            elif midPl > addr: high = mid - 1
            else: return midPl
        return None

    def getPlayersInLobby(self, exclude = None):
        playersInLobby = []
        for player in self.players:
            if player.getRoomId() == -1 and player != exclude:
                playersInLobby.append(player)
        return playersInLobby

    def sortPlayers(self):
        self.players.sort(cmp=lambda x,y: x.getPlayerNo() - y.getPlayerNo())

    def controlThread(self):
        while self.running:
            inp = raw_input(">>> ")
            if inp == "players":
                print "%d players connected" % len(self.players)
            elif inp == "rooms":
                print "%d active rooms" % len(self.rooms)
            elif inp == "quit":
                print "Stopping server, please wait..."
                self.stopServer()
            elif inp == "restart":
                print "Stopping server, please wait..."
                self.restart = True
                self.stopServer()

    def stopServer(self):
        self.running = False
        for r in self.rooms:
            r.state = "DEAD"

    def out(self, string):
        print "SERVER:", string
        print ">>> ",

    def addPlayer(self, playerAddr, playerName):
        np = Player(self, self.nextPlayerId, playerAddr, playerName)
        self.nextPlayerId += 1
        #self.players.append(np)
        bisect.insort(self.players, np)
        
        np.sendPlayerList(self.getPlayersInLobby(), -1, 0)
        np.sendRoomList(self.rooms)

        for player in self.getPlayersInLobby(np):
            if player == np: continue
            player.sendNewPlayer(np)

        return np

    def addRoom(self, roomName, hostPlayer):
        newroom = Room(self, roomName, self.nextRoomId)
        self.nextRoomId += 1
        self.rooms.append(newroom)
        bisect.insort(self.rooms, newroom)
        if newroom.join(hostPlayer):
            self.leave(hostPlayer, False)
        else:
            #If it every comes to this, expect problems
            hostPlayer.sendDataReliable(Structs.leaveRoom.dataType, "")

        self.sendRooms()

    def joinRoom(self,rid,player):
        room = self.getRoom(rid)
        success = False
        if room != None:
            if room.join(player):
                success = True
        if success:
            self.leave(player, False)
        else:
            player.sendDataReliable(Structs.leaveRoom.dataType, "")
            
    def leaveRoom(self,player):
        if player.getRoomId() != -1:
             self.getRoom(player.getRoomId()).leave(player)
             player.sendPlayerList(self.getPlayersInLobby(), -1, 0)
             player.sendRoomList(self.rooms)

    def removeRoom(self, room):
        self.rooms.remove(room)
        self.sendRooms()

    def leave(self, player, disconnected=False):
        if disconnected: self.removePlayer(player)
        pInL = self.getPlayersInLobby()
        for lobbyPlayer in pInL:
            lobbyPlayer.sendPlayerLeft(player)
        

    def removePlayer(self, player):
        if player in self.players:  
            self.players.remove(player)
            player.connected = False
        else: self.out("Tried to remove nonexisting player")

    def sendData(self, data, addr):
        self.sock.sendto(data, addr)

    def sendRooms(self):
        playerList = self.getPlayersInLobby()
        for player in playerList:
            player.sendRoomList(self.rooms)

    def disconnectPlayer(self, player):
        if player.connected:
            self.getRoom(player.getRoomId()).leave(player, True)

    def mainloop(self):
        self.running = True
        ctrlThread = Thread(target = self.controlThread)
        ctrlThread.start()
        while self.running:
            read, write, error = select([self.sock], [], [], settings.POLL_INTERVAL)
            if len(read) == 0: # There is no data for me to process
                continue
            readsock = read[0]
            try:
                rawdata, addr = readsock.recvfrom(self.buf)
            except:
                continue
            #There are 14 potential different types of data to handle
            #datatype is all in the first byte
            dataType = Structs.dataType.unpack(rawdata[:Structs.dataType.size])[0]
            reliableId = Structs.dataType.unpack(rawdata[:Structs.dataType.size])[1]
            data = rawdata[Structs.dataType.size:]
            player = self.getPlayerByAddr(addr)

            #if player == None:
            #    if len(self.pending_players) != 0:
            #        for p in self.pending_players:
            #            if addr == p:
            #                player = p
            #                break
                        
            if player == None and dataType != Structs.connect.dataType:
                self.out("Unknown player " + str(addr) + " sent message")
                continue

            if player != None:
                player.lastTime = time()

            sendResponse = True
            if dataType == Structs.connect.dataType:
                nameSz = Structs.connect.unpack(data[:Structs.connect.size])[0]
                name = data[Structs.connect.size:Structs.connect.size+nameSz]
                player = self.addPlayer(addr, name)
                self.out("Player %s connected" % str(addr))
            elif dataType == Structs.preChat.dataType:
                datSz = Structs.preChat.unpack(data[:Structs.preChat.size])[0]
                chatMsg = data[Structs.preChat.size:Structs.preChat.size+datSz]
                player.sendChatMsg(chatMsg)            
            elif dataType == Structs.makeRoom.dataType:
                nameSz = Structs.makeRoom.unpack(data[:Structs.makeRoom.size])[0]
                roomName = data[Structs.makeRoom.size:Structs.makeRoom.size+nameSz]
                self.addRoom(roomName, player)
            elif dataType == Structs.joinRoom.dataType:
                self.joinRoom(Structs.joinRoom.unpack(data)[0], player)
            elif dataType == Structs.leaveRoom.dataType:
                self.leaveRoom(player)
            elif dataType == Structs.startGame.dataType:
                if player.getRoomId() != -1:
                    self.getRoom(player.getRoomId()).startGame(player)
            elif dataType == Structs.playerDat.dataType:
                player.setGameData(data)
                sendResponse = False
            elif dataType == Structs.shoot.dataType:
                player.sendShoot(Structs.shoot.unpack(data), self.getRoom(player.getRoomId()).getPlayers(player))
            elif dataType == Structs.gotData.dataType:
                player.setGotData(Structs.gotData.unpack(data)[1])
                sendResponse = False
            elif dataType == Structs.disconnect.dataType:
                self.getRoom(player.getRoomId()).leave(player, True)
                self.out("Player %s disconnected" % str(addr))
            elif dataType == Structs.setCharacter.dataType:
                player.setCharId(Structs.setCharacter.unpack(data)[0])
            elif dataType == Structs.onDeath.dataType:
                killerid = Structs.onDeath.unpack(data)[0]
                self.getRoom(player.getRoomId()).manageDeath(player, killerid)
            elif dataType == Structs.takeWeap.dataType:
                svId = Structs.takeWeap.unpack(data)[0]
                self.getRoom(player.getRoomId()).pickupWeap(svId)
            if sendResponse and reliableId != 0:
                player.sendData(Structs.dataType.pack(Structs.gotData.dataType, 0) +
                                Structs.gotData.pack(dataType, reliableId))

            for player in self.players:
                if (time() - player.lastTime) > settings.PLAYERTIMEOUT:
                    self.getRoom(player.getRoomId()).leave(player, True)
        self.sock.close()
                
                                                        
if __name__ == "__main__":
    random.seed(os.urandom(64))
    restart = True
    port = sys.argv[1] if len(sys.argv) > 1 else settings.LISTEN_PORT
    try: 
        int(port)
    except ValueError:
        print "Error: Invalid port number."
        exit()
    while restart:
        server = Server(settings.LISTEN_HOST, port)
        server.mainloop()
        restart = server.restart
    print "Server stopped"
    
    
                    
                    
                
                
            
