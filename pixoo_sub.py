import zmq
import logging
from datetime import timedelta
from typing import Dict, Any

from pixoo import Pixoo
from hud_renderer import HUDRenderer
from config import PIXOO_IP, ZMQ_SUBSCRIBE_ADDR, ZMQ_SUBSCRIBE_TOPIC

# Logging Setup
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Pixoo Setup
pixoo = Pixoo(PIXOO_IP)

# ZeroMQ Setup
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(ZMQ_SUBSCRIBE_ADDR)
socket.setsockopt_string(zmq.SUBSCRIBE, ZMQ_SUBSCRIBE_TOPIC)


def format_hero_name(raw_name: str) -> str:
    base = raw_name.replace("npc_dota_hero_", "")
    return " ".join(word.capitalize() for word in base.split("_"))


def get_game_details(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant hero/player/map info from GSI payload.
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

    clock_time = data.get("map", {}).get("clock_time", 0)
    time_str = str(timedelta(seconds=max(0, int(clock_time))))

    # Filter inventory to include only specific slots.
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
    # Instantiate the HUDRenderer.
    hud_renderer = HUDRenderer()

    while True:
        try:
            data = socket.recv_json()
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

        except Exception as e:
            logging.exception("[!] Error while updating Pixoo display")


if __name__ == "__main__":
    main()
