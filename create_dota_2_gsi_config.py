import os
import logging
from textwrap import dedent
from config import (
    GSI_RECEIVER_IP,
    GSI_RECEIVER_PORT,
    STEAM_GSI_CONFIG_DIR,
    GSI_CONFIG_FILENAME,
    UPDATE_INTERVAL,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def create_gsi_config(
    ip: str = GSI_RECEIVER_IP,
    port: int = GSI_RECEIVER_PORT,
    path: str = STEAM_GSI_CONFIG_DIR,
    filename: str = GSI_CONFIG_FILENAME,
) -> None:
    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Ensured directory exists: {path}")
    except Exception as e:
        logging.error(f"Failed to create directory '{path}': {e}")
        return

    config_path = os.path.join(path, filename)

    config_content = dedent(
        f"""
        "Custom GSI Configuration"
        {{
            "uri" "http://{ip}:{port}/"
            "timeout" "5.0"
            "buffer"  "{UPDATE_INTERVAL}"
            "throttle" "{UPDATE_INTERVAL}"
            "heartbeat" "30.0"
            "data"
            {{
                "provider"   "1"
                "map"        "0"
                "player"     "1"
                "hero"       "1"
                "abilities"  "0"
                "items"      "1"
                "wearables"  "0"
                "auth"       "0"
                "draft"      "0"
                "buildings"  "0"
                "allplayers" "0"
            }}
        }}
    """
    ).strip()

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        logging.info(f"GSI config written to: {config_path}")
    except Exception as e:
        logging.error(f"Failed to write GSI config to '{config_path}': {e}")


if __name__ == "__main__":
    create_gsi_config()
