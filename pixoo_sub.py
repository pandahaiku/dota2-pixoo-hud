import zmq
import logging
import time
import requests
from datetime import timedelta
from typing import Dict, Any
from pixoo import Pixoo
from hud_renderer import HUDRenderer
from dota_game_states import GameState
from config import PIXOO_IP, ZMQ_SUBSCRIBE_ADDR, ZMQ_SUBSCRIBE_TOPIC, GSI_TIMEOUT


def get_pixoo_channel(ip: str) -> int:
    """
    Retrieves the current channel index from the Pixoo device.
    Returns:
        int: The current channel index, or channel 0 if retrieval fails.
    """
    try:
        payload = {"Command": "Channel/GetIndex"}
        response = requests.post(f"http://{ip}/post", json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("SelectIndex", 0)
    except Exception as e:
        print(f"[!] Failed to get Pixoo channel: {e}")
        return 0


def switch_to_divoom_channel(ip: str, channel_index: int = 1):
    """
    Switch Pixoo display to a built-in channel.
    Common channels:
        0 = Faces
        1 = Cloud Channel (Divoom App)
        2 = Visualizer
        3 = Custom (API-controlled)
    """
    try:
        payload = {"Command": "Channel/SetIndex", "SelectIndex": channel_index}
        response = requests.post(f"http://{ip}/post", json=payload, timeout=5)
        response.raise_for_status()
        print(f"[✅] Switched to Pixoo channel {channel_index}")
    except Exception as e:
        print(f"[!] Failed to switch channel: {e}")


original_channel = get_pixoo_channel(PIXOO_IP)
print(f"Original Pixoo channel: {original_channel}")


# Set up logging format
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Initialize Pixoo display using its IP address
pixoo = Pixoo(PIXOO_IP)

# Set up ZeroMQ subscriber socket to receive GSI updates
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(ZMQ_SUBSCRIBE_ADDR)
socket.setsockopt_string(zmq.SUBSCRIBE, ZMQ_SUBSCRIBE_TOPIC)
socket.RCVTIMEO = GSI_TIMEOUT  # Set socket receive timeout (5 seconds)


def format_hero_name(raw_name: str) -> str:
    """
    Convert raw hero ID from Dota (e.g., 'npc_dota_hero_juggernaut') into readable format ('Juggernaut').
    """
    base = raw_name.replace("npc_dota_hero_", "")
    return " ".join(word.capitalize() for word in base.split("_"))


def get_game_details(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key hero, player, and map details from the GSI JSON payload.
    """
    hero_data = data.get("hero", {})
    raw_hero_id = hero_data.get("name", "npc_dota_hero_unknown")
    hero_name = format_hero_name(raw_hero_id)
    level = hero_data.get("level", 0)

    hp = hero_data.get("health", 0)
    max_hp = hero_data.get("max_health", 1)
    hp_ratio = hp / max_hp if max_hp else 0

    mana = hero_data.get("mana", 0)
    max_mana = hero_data.get("max_mana", 1)
    mana_ratio = mana / max_mana if max_mana else 0

    player = data.get("player", {})
    kills = player.get("kills", 0)
    deaths = player.get("deaths", 0)
    assists = player.get("assists", 0)
    gold = player.get("gold", 0)

    # Convert clock time (seconds) into HH:MM:SS string
    clock_time = data.get("map", {}).get("clock_time", 0)
    time_str = str(timedelta(seconds=max(0, int(clock_time))))

    # Filter item slots to show only relevant gear (no empty or unused slots)
    all_items = data.get("items", {})
    relevant_slots = [
        "slot0",
        "slot1",
        "slot2",
        "slot3",
        "slot4",
        "slot5",
        "teleport0",
        "neutral0",
    ]
    filtered_items = {
        slot: all_items[slot]
        for slot in relevant_slots
        if slot in all_items and all_items[slot].get("name") != "empty"
    }

    return {
        "hero_id": raw_hero_id,
        "hero_name": hero_name,
        "level": level,
        "hp_ratio": hp_ratio,
        "mana_ratio": mana_ratio,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "time_str": time_str,
        "items": filtered_items,
        "gold": gold,
    }


def main() -> None:
    logging.info("🟢 Pixoo Dota 2 HUD listener started.")
    hud_renderer = HUDRenderer()
    prev_game_state = None
    last_update_time = time.time()

    while True:
        try:
            data = socket.recv_json()
            last_update_time = time.time()  # Record last successful message

            # Parse game state
            map_data = data.get("map", {})
            raw_game_state = map_data.get("game_state", "UNKNOWN")
            game_state = (
                GameState(raw_game_state)
                if raw_game_state in GameState._value2member_map_
                else GameState.UNKNOWN
            )

            # Check if game state has changed
            if game_state != prev_game_state:
                logging.info(
                    f"[📺] Game state changed: {prev_game_state} ➜ {game_state}"
                )
                prev_game_state = game_state

                if game_state in [GameState.PRE_GAME, GameState.GAME_IN_PROGRESS]:
                    logging.info("[🏁] Match has started!")
                    pixoo.set_channel(0)
                elif game_state in [GameState.POST_GAME, GameState.UNKNOWN]:
                    logging.info("[✅] Match has ended or state unknown.")
                    switch_to_divoom_channel(PIXOO_IP, original_channel)

            # Update HUD if actively in-game
            if game_state in [GameState.PRE_GAME, GameState.GAME_IN_PROGRESS]:
                details = get_game_details(data)
                img = hud_renderer.create_base_layout(
                    hero_name=details["hero_id"],
                    level=details["level"],
                    hp=details["hp_ratio"],
                    mana=details["mana_ratio"],
                    items=details["items"],
                    kills=details["kills"],
                    deaths=details["deaths"],
                    assists=details["assists"],
                    gold=details["gold"],
                )
                pixoo.draw_image(img)
                pixoo.push()

        except zmq.error.Again:
            # Timeout occurred — check how long it's been since last GSI update
            if time.time() - last_update_time > GSI_TIMEOUT / 1000:
                logging.warning(
                    f"⏱️ No data received in {GSI_TIMEOUT / 1000}s. Assuming Dota 2 was closed."
                )
                switch_to_divoom_channel(PIXOO_IP, original_channel)
                logging.warning(f"Closing Script. Goodbye! 👋")
                exit()
        except Exception as e:
            logging.exception("[!] Unexpected error while updating Pixoo display")


if __name__ == "__main__":
    main()
