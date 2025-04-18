from enum import Enum

class GameState(Enum):
    UNKNOWN = "UNKNOWN"
    DISCONNECTED = "DOTA_GAMERULES_STATE_DISCONNECT"
    WAIT_FOR_PLAYERS = "DOTA_GAMERULES_STATE_WAIT_FOR_PLAYERS_TO_LOAD"
    HERO_SELECTION = "DOTA_GAMERULES_STATE_HERO_SELECTION"
    STRATEGY_TIME = "DOTA_GAMERULES_STATE_STRATEGY_TIME"
    PRE_GAME = "DOTA_GAMERULES_STATE_PRE_GAME"
    GAME_IN_PROGRESS = "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS"
    POST_GAME = "DOTA_GAMERULES_STATE_POST_GAME"
    CUSTOM_GAME_SETUP = "DOTA_GAMERULES_STATE_CUSTOM_GAME_SETUP"
