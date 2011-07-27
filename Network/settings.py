MAX_PLAYERS = 32 # Maximum players in a room
POLL_INTERVAL = 0.001 # Wait time for select function
MAX_TRIES = 5 # Maximum number of times data should be resent
SEND_WAIT = 1 # Seconds to wait before expecting response from client
GAME_INTERVAL = .05 # How often game data should be sent (GAME_INTERVAL = 1/TIMES_PER_SEC)
PLAYERTIMEOUT = 600 # Seconds before player timeout

## SERVER
LISTEN_HOST = "" # Hostname / IP address server should bind to
LISTEN_PORT = 62227 # Port server should bind to

## CLIENT (Not used anymore)
#SERVER_HOST = "localhost" # Name of host client should connect to
#SERVER_PORT = 62227 # Port of server client should connect to

def formatChat(name, message):
    return "%s: %s" % (name, message)
