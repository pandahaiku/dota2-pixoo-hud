import os
import logging
import requests
from PIL import Image, ImageEnhance
from typing import Tuple
from config import (
    HERO_CACHE_DIR,
    ITEM_CACHE_DIR,
    GOLD_ICON_PATH,
    HERO_URL_TEMPLATE,
    ITEM_URL_TEMPLATE,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# In-memory caches
HEROPORTRAIT_CACHE: dict[str, Image.Image] = {}
ITEMICON_CACHE: dict[str, Image.Image] = {}
BRIGHTEN_CACHE: dict[Tuple[int, float], Image.Image] = {}
GOLDICON_CACHE: dict[Tuple[int, int], Image.Image] = {}


def get_hero_portrait_cached(hero_name: str) -> Image.Image:
    """
    Download and cache a resized Dota 2 hero portrait.
    """
    hero_id = hero_name.replace("npc_dota_hero_", "")

    # Fallback for undefined hero
    if hero_id == "unknown":
        logging.warning("[!] Hero is unknown — using fallback portrait")
        return Image.new("RGBA", (41, 25), (50, 50, 50, 255))

    if hero_id in HEROPORTRAIT_CACHE:
        return HEROPORTRAIT_CACHE[hero_id]

    os.makedirs(HERO_CACHE_DIR, exist_ok=True)
    local_path = os.path.join(HERO_CACHE_DIR, f"{hero_id}.png")

    if not os.path.exists(local_path):
        url = f"{HERO_URL_TEMPLATE}/{hero_id}.png"
        logging.info(f"[↓] Downloading hero portrait: {url}")
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)

    img = (
        Image.open(local_path)
        .convert("RGBA")
        .resize((41, 25), Image.Resampling.LANCZOS)
    )
    HEROPORTRAIT_CACHE[hero_id] = img
    return img


def get_item_icon_cached(
    item_name: str, size: Tuple[int, int] = (15, 15)
) -> Image.Image:
    """
    Download and cache a resized Dota 2 item icon.
    """
    item_id = item_name.replace("item_", "")
    if item_id in ITEMICON_CACHE:
        return ITEMICON_CACHE[item_id]

    os.makedirs(ITEM_CACHE_DIR, exist_ok=True)
    local_path = os.path.join(ITEM_CACHE_DIR, f"{item_id}.png")

    if not os.path.exists(local_path):
        url = f"{ITEM_URL_TEMPLATE}/{item_id}.png"
        logging.info(f"[↓] Downloading item icon: {url}")
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)

    img = Image.open(local_path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    ITEMICON_CACHE[item_id] = img
    return img


def brighten_image_cached(img: Image.Image, factor: float = 1.5) -> Image.Image:
    """
    Return a brightened version of the image, using a cache for repeated enhancements.
    """
    key = (id(img), factor)
    if key in BRIGHTEN_CACHE:
        return BRIGHTEN_CACHE[key]

    enhanced_img = ImageEnhance.Brightness(img).enhance(factor)
    BRIGHTEN_CACHE[key] = enhanced_img
    return enhanced_img


def get_gold_icon_resized(size: Tuple[int, int] = (12, 12)) -> Image.Image:
    """
    Load and resize the gold icon from the assets directory.
    Uses an in-memory cache for resized versions.
    """
    if size in GOLDICON_CACHE:
        return GOLDICON_CACHE[size]

    if not os.path.exists(GOLD_ICON_PATH):
        raise FileNotFoundError(f"Gold icon not found at path: {GOLD_ICON_PATH}")

    img = (
        Image.open(GOLD_ICON_PATH)
        .convert("RGBA")
        .resize(size, Image.Resampling.LANCZOS)
    )
    GOLDICON_CACHE[size] = img
    return img
