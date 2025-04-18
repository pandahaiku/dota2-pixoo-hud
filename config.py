import os
from os.path import expanduser

# Dynamically determine the project root (one level up from this file)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Paths to assets and cached resources
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")

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
PIXOO_IP = "192.168.68.65"

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
GSI_TIMEOUT = (
    5000  # Max time (in milliseconds) to wait for a GSI message before assuming no data
)

# Dota 2 CDN Details
GOLD_ICON_PATH = os.path.join(ASSETS_DIR, "gold.png")
HERO_CACHE_DIR = os.path.join(CACHE_DIR, "heroes")
ITEM_CACHE_DIR = os.path.join(CACHE_DIR, "items")
HERO_URL_TEMPLATE = (
    "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes"
)
ITEM_URL_TEMPLATE = (
    "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items"
)
