import settings
import time
import Structs
import socket
from time import sleep
from select import select
from threading import Thread

class Client(object):
    sock = None
    running = False
    dataThread = None
    server = None
    buf = 2048
    nRid = 0
    unrecievedMsg = []
    connected = False
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.unrecievedMsg = []

    def connect(self, name, addr):
        self.server = addr
        self.running = True
        self.dataThread = Thread(target = self.data)
        self.dataThread.start()
        t = self.sendDataReliable(Structs.connect.dataType, Structs.connect.pack(len(name))+name)
        t.join()
        return self.connected
        
    def disconnect(self):
        self.running = False
        if self.connected:
            self.sendDataReliable(Structs.disconnect.dataType, "").join()
            self.connected = False
        self.sock.close()

    def isConnected(self):
        return self.connected

    def getNextReliableId(self):
        self.nRid += 1
        if self.nRid >= 65536:
            self.nRid = 1
        return self.nRid
    
    def onRoomInfo(self, data):
        self.out(data)

    def onPlayerList(self, playerList, roomId, roomState, yourId):
        self.out("PlayerList: " + str(playerList))

    def onNewPlayer(self, player):
        self.out(player)

    def onPlayerLeft(self, player):
        self.out(player)

    def onRoomList(self, roomList):
        self.out(roomList)

    def onWeapList(self, weapList):
        self.out(weapList)

    def onChat(self, data):
        self.out(data)

    def onPlayerData(self, playerData):
        self.out(playerData)

    def onRoomStat(self, data):
        self.out(data)

    def onLeaveRoom(self, data):
        self.out(data)

    def onShoot(self, data):
        self.out(data)

    def onScore(self, data):
        self.out(data)

    def onChangeChar(self, charId, playerId):
        self.out(charId, playerId)
        
    def onDisconnect(self):
        self.out("I was disconnected.")
    

    def _onDisconnect(self):
        self.connected = False
        self.running = False
        self.onDisconnect()

    def sendData(self, dataType, data):
        self.sock.sendto(Structs.dataType.pack(dataType, 0) + data, self.server)

    def sendDataReliableThread(self, rid, data):
        for i in xrange(settings.MAX_TRIES):
            #self.sendData(data)
            self.sock.sendto(data, self.server)
            sleep(settings.SEND_WAIT)
            if not rid in self.unrecievedMsg:
                return
            if not self.running:
                return
            
        if self.connected:
            self._onDisconnect()
            
    def sendDataReliable(self, dataType, data):
        rid = self.getNextReliableId()
        preDat = Structs.dataType.pack(dataType, rid)
        data = preDat + data
        self.unrecievedMsg.append(rid)
        t = Thread(target = self.sendDataReliableThread, args=[rid, data])
        t.start()
        return t
    
    def out(self, string):
        print " "
        print string
        print ":",
        
    def data(self):
        while self.running:
            read, write, error = select([self.sock], [], [], settings.POLL_INTERVAL)
            if len(read) == 0: # There is no data for me to process
                continue
            readsock = read[0]
            try:
                rawdata, addr = readsock.recvfrom(self.buf)
            except socket.error:
                if self.connected:
                    self._onDisconnect()
                self.running = False
                break
            self.connected = True
            #There are 14 potential different types of data to handle
            #datatype is all in the first byte
            dataType = Structs.dataType.unpack(rawdata[:Structs.dataType.size])[0]
            reliableId = Structs.dataType.unpack(rawdata[:Structs.dataType.size])[1]
            data = rawdata[Structs.dataType.size:]

            sendResponse = True
            #print rawdata
            if dataType == Structs.playerInfo.dataType:
                sendResponse = False #Don't think I need this
            elif dataType == Structs.roomInfo.dataType:
                self.onRoomInfo(Structs.roomInfo.unpack(data))
            elif dataType == Structs.prePlayerList.dataType:
                upckd = Structs.prePlayerList.unpack(data[:Structs.prePlayerList.size])
                sizePl = upckd[0]
                roomId = upckd[1]
                roomState = upckd[2]
                yourId = upckd[3]
                pllist_raw = data[Structs.prePlayerList.size:]
                pllist = []
                i = 0
                while i < sizePl:
                    playerInfo_s = pllist_raw[i:i+Structs.playerInfo.size]
                    playerInfo = Structs.playerInfo.unpack(playerInfo_s)
                    nameSize = playerInfo[2]
                    endInf = i+Structs.playerInfo.size
                    name = pllist_raw[endInf:endInf+nameSize]
                    playerInfo = playerInfo + (name,)
                    pllist.append(playerInfo)
                    i += len(playerInfo_s) + nameSize
                    
                self.onPlayerList(pllist, roomId, roomState, yourId)
            elif dataType == Structs.preRoomList.dataType:
                sizeRm = Structs.preRoomList.unpack(data[:Structs.preRoomList.size])[0]
                rmlist_raw = data[Structs.preRoomList.size:]
                rmlist = []
                i = 0
                while i < sizeRm:
                    roomInfo_s = rmlist_raw[i:i+Structs.roomInfo.size]
                    roomInfo = Structs.roomInfo.unpack(roomInfo_s)
                    nameSize = roomInfo[4]

                    endInf = i+Structs.roomInfo.size
                    name = rmlist_raw[endInf:endInf+nameSize]
                    roomInfo = roomInfo + (name,)
                    rmlist.append(roomInfo)
                    i += len(roomInfo_s) + nameSize
                self.onRoomList(rmlist)
            elif dataType == Structs.preChat.dataType:
                sizeChat = Structs.preChat.unpack(data[:Structs.preChat.size])[0]
                self.onChat(data[Structs.preChat.size:Structs.preChat.size+sizeChat])
            elif dataType == Structs.prePlayerDat.dataType:
                sizeDa = Structs.prePlayerDat.unpack(data[:Structs.prePlayerDat.size])[0] / Structs.playerDat.size
                dalist_raw = data[Structs.prePlayerDat.size:]
                dalist = []
                for i in xrange(sizeDa):
                    parse = dalist_raw[i*Structs.playerDat.size:(i+1)*Structs.playerDat.size]
                    dalist.append(Structs.playerDat.unpack(parse))
                self.onPlayerData(dalist)
            elif dataType == Structs.shoot.dataType:
                self.onShoot(Structs.shoot.unpack(data))
            elif dataType == Structs.updateRoomStat.dataType:
                self.onRoomStat(Structs.updateRoomStat.unpack(data))
            elif dataType == Structs.leaveRoom.dataType:
                self.onLeaveRoom()
            elif dataType == Structs.newPlayer.dataType:
                mainDat = Structs.newPlayer.unpack(data[:Structs.newPlayer.size])
                mainDat = mainDat + (data[Structs.newPlayer.size:Structs.newPlayer.size+mainDat[2]],)
                self.onNewPlayer(mainDat)
            elif dataType == Structs.playerLeft.dataType:
                dataunpck = Structs.playerLeft.unpack(data[:Structs.playerLeft.size])
                name = data[Structs.playerLeft.size:Structs.playerLeft.size+dataunpck[1]]
                self.onPlayerLeft(dataunpck+(name,))
            elif dataType == Structs.gotData.dataType:
                try:
                    self.unrecievedMsg.remove(Structs.gotData.unpack(data)[1])
                except: pass
                sendResponse = False
            elif dataType == Structs.sendScore.dataType:
                self.onScore(Structs.sendScore.unpack(data))
            elif dataType == Structs.preWeapon.dataType:
                sizeWp = Structs.preWeapon.unpack(data[:Structs.preWeapon.size])[0]
                wplist_raw = data[Structs.preWeapon.size:]
                wplist = []
                for i in xrange(sizeWp):
                    j = i*Structs.weapon.size
                    weapInfo_s = wplist_raw[j:j+Structs.weapon.size]
                    wplist.append(Structs.weapon.unpack(weapInfo_s))
                self.onWeapList(wplist)
            elif dataType == Structs.setCharacter.dataType:
                charId,playerId = Structs.setCharacter.unpack(data)
                self.onChangeChar(charId,playerId)

                
            if sendResponse and reliableId != 0:
                self.sendData(Structs.gotData.dataType,
                                      Structs.gotData.pack(dataType, reliableId))

    def __del__(self):
        print "del"
        self.disconnect()
            
                
                    
            
if __name__ == "__main__":
    client = Client()
    name = raw_input("Enter your name: ")
    j = client.connect(name, ("localhost", 62227))
    if not j:
        print "Connection failed"
    while client.isConnected():
        inp = raw_input(": ")
        if inp == "quit":
            client.disconnect()
            break
        if inp[:4] == "chat":
            data = [Structs.preChat.pack(len(inp[5:])),
                    name + ": " + inp[5:]]
            client.sendDataReliable(Structs.preChat.dataType, ''.join(data))
            
            
