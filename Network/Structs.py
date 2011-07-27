from struct import Struct as BaseStruct

dt = 0
def diD():
    global dt
    r = dt
    dt += 1
    return r

class Struct(BaseStruct):
    dataType = -1
    
    def __init__(self, fmt, datatype):
        super(Struct, self).__init__(fmt)
        self.dataType = datatype

#0
dataType = Struct("!BH", diD()) # Datatype, ReliableId
connect = Struct("!H", diD()) # Name size

playerInfo = Struct("!hBBBB", diD()) # Player Id, Player Number, Name Size, Character Id, isMaster
roomInfo = Struct("!hBBBBB", diD()) # Room Id, Players, Max Players, Room State, Name Size, Extra

prePlayerList = Struct("!HhBh", diD()) # Size, Room Id, Room State, callingPlayer's Id
#5
preRoomList = Struct("!H", diD()) # Size

preChat = Struct("!H", diD()) # Size

makeRoom = Struct("!H", diD()) # Room name size
joinRoom = Struct("!h", diD()) # Room Id
leaveRoom = Struct("", diD()) #

#10
startGame = Struct("!B", diD()) #

prePlayerDat = Struct("!H", diD()) #Size
playerDat = Struct("!hhfffffB", diD()) # Player Id, Weapon Id, x, y, rotation, mousedist,mouseang, Animation

shoot = Struct("!hiifB", diD()) # Player Id, x, y, angle, bulletType
updateRoomStat = Struct("!Bh", diD()) # State, winnerId

#addPlayer = Struct("!32shBBB", diD()) # Name , Player Id, Player Number, Character Id, Extra
#15
gotData = Struct("!BB", diD()) # Datatype, ReliableId
disconnect = Struct("", diD()) #
playerLeft = Struct("!hHh", diD()) # Player Id, Player name size, newMaster Id
newPlayer = Struct("!hBBBB", diD()) # Player Id, Player Number, Name Size, Character Id, Extra

setCharacter = Struct("!Bh", diD()) # Character Id, PlayerId

#20
onDeath = Struct("!h", diD()) # Killer id
sendScore = Struct("!hhhhhh", diD()) # Player id, Kills, Deaths, Player2 id, Kills, Deaths

preWeapon = Struct("!H", diD()) # Size
weapon = Struct("!hbff", diD()) # Server Weap Id, Weapon Id, Weap X, Weap Y
takeWeap = Struct("!h", diD()) # Server Weap Id
