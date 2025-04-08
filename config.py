from os.path import expanduser

# IP and port for receiving GSI data
GSI_RECEIVER_IP = "127.0.0.1"
GSI_RECEIVER_PORT = 3000

# Flask settings
LOCAL_DOTA_HOST = "0.0.0.0"
LOCAL_DOTA_PORT = 3000
DEBUG_MODE = False

# ZeroMQ settings
ZMQ_PUB_PORT = 5555
ZMQ_PUB_BIND_ADDR = f"tcp://*:{ZMQ_PUB_PORT}"

# Pixoo display IP
PIXOO_IP = "192.168.68.75"

# ZeroMQ subscriber config
ZMQ_SUBSCRIBE_ADDR = "tcp://localhost:5555"
ZMQ_SUBSCRIBE_TOPIC = ""  # Subscribe to all topics

# Path to Steam's Dota 2 GSI config directory (customize if needed)
STEAM_GSI_CONFIG_DIR = expanduser(
    "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/cfg/gamestate_integration"
)

# Name of the config file to create
GSI_CONFIG_FILENAME = "gamestate_integration_custom.cfg"

# GSI Config Details
UPDATE_INTERVAL = "1"  # In seconds, how often data is sent from GSI

# Dota 2 CDN Details
HERO_CACHE_DIR = "cache/heroes"
ITEM_CACHE_DIR = "cache/items"
GOLD_ICON_PATH = "assets/gold.png"
HERO_URL_TEMPLATE = (
    "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes"
)
ITEM_URL_TEMPLATE = (
    "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items"
)
