from PIL import Image, ImageDraw, ImageFont
import json
from typing import Dict, Tuple, Any
from dota_2_cdn import (
    get_hero_portrait_cached,
    get_item_icon_cached,
    brighten_image_cached,
    get_gold_icon_resized,
)

# Global Caches
STATIC_LAYER_CACHE: Dict[str, Image.Image] = {}
GLOBAL_LAST_INVENTORY_KEY: Any = None
GLOBAL_CACHED_INVENTORY_IMAGE: Any = None

# Inventory Layout Constants
ITEM_SIZE = 12  # intended target size for item icons (used for resizing)
PADDING = 2  # extra spacing added to each slot
COLS = 3
ROWS = 2
# Each slot width/height is based on the icon size minus 1 plus the padding
SLOT_W = ITEM_SIZE - 1 + PADDING
SLOT_H = ITEM_SIZE - 1 + PADDING
# Total grid dimensions: (number of columns/rows * individual slot dimension) minus the extra padding
GRID_W = COLS * SLOT_W - PADDING
GRID_H = ROWS * SLOT_H - PADDING
GRID_ORIGIN: Tuple[int, int] = (2, 39)  # where the grid is placed on the static layer

# Slot Mapping
slot_to_position: Dict[str, Tuple[int, int]] = {
    "slot0": (0, 0),
    "slot1": (1, 0),
    "slot2": (2, 0),
    "slot3": (0, 1),
    "slot4": (1, 1),
    "slot5": (2, 1),
}


# Font Loading
def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """
    Attempt to load a TrueType font, falling back to a default font on error.
    """
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


# Preloaded fonts
CONSOLA_FONT_10 = load_font("consola.ttf", 10)
CONSOLA_FONT_9 = load_font("consola.ttf", 9)
CONSOLA_FONT_8 = load_font("consola.ttf", 8)
VERDANA_FONT_9 = load_font("verdana.ttf", 9)
VERDANA_FONT_8 = load_font("verdana.ttf", 8)


# Inventory Grid Drawing
def draw_inventory_borders(draw: ImageDraw.Draw, origin: Tuple[int, int]) -> None:
    """
    Draw the inventory grid background, borders, and inner dividers onto the given drawing context.
    """
    inv_x, inv_y = origin

    # Fill the inventory area with a dark gray background
    draw.rectangle(
        [inv_x - 1, inv_y - 1, inv_x + GRID_W, inv_y + GRID_H], fill=(30, 30, 30)
    )
    # Draw left and right vertical borders
    for i in range(2):
        # Left border lines at x = inv_x - 2 and x = inv_x - 1
        draw.line(
            [(inv_x - 2 + i, inv_y - 1), (inv_x - 2 + i, inv_y + GRID_H)],
            fill=(100, 100, 100),
        )
        # Right border lines at x = inv_x + GRID_W and x = inv_x + GRID_W + 1
        draw.line(
            [(inv_x + GRID_W + i, inv_y - 1), (inv_x + GRID_W + i, inv_y + GRID_H)],
            fill=(100, 100, 100),
        )
    # Draw top and bottom horizontal borders
    draw.line(
        [(inv_x - 2, inv_y - 1), (inv_x + GRID_W + 1, inv_y - 1)], fill=(100, 100, 100)
    )
    draw.line(
        [(inv_x - 2, inv_y + GRID_H), (inv_x + GRID_W + 1, inv_y + GRID_H)],
        fill=(100, 100, 100),
    )
    # Inner grid dividers
    for i in range(1, COLS):
        x = inv_x + i * SLOT_W - PADDING // 2
        draw.line([(x, inv_y), (x, inv_y + GRID_H)], fill=(100, 100, 100))
    for j in range(1, ROWS):
        y = inv_y + j * SLOT_H - PADDING // 2
        draw.line([(inv_x, y), (inv_x + GRID_W, y)], fill=(100, 100, 100))


# Static Layer
def create_static_layer(hero_name: str) -> Image.Image:
    """
    Create the static overlay for the HUD (hero portrait, bars, K/D/A labels, level circle, and inventory grid).
    """
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)

    # Add hero portrait with brightness enhancement
    portrait = brighten_image_cached(get_hero_portrait_cached(hero_name), 1.3)
    canvas.paste(portrait, (0, 0))

    # Draw HP and Mana bar backgrounds
    draw.rectangle([0, 26, 40, 30], fill=(50, 50, 50))
    draw.rectangle([0, 32, 40, 36], fill=(50, 50, 50))

    # Draw static K/D/A labels (no dynamic numbers)
    kda_x = 43
    draw.text((kda_x, 0), "K", font=CONSOLA_FONT_10, fill=(0, 255, 0))
    draw.text((48, -2), ":", font=VERDANA_FONT_9, fill=(0, 255, 0))
    draw.text((kda_x, 8), "D", font=CONSOLA_FONT_10, fill=(255, 68, 68))
    draw.text((48, 6), ":", font=VERDANA_FONT_9, fill=(255, 68, 68))
    draw.text((kda_x, 16), "A", font=CONSOLA_FONT_10, fill=(128, 248, 255))
    draw.text((48, 14), ":", font=VERDANA_FONT_9, fill=(128, 248, 255))

    # Static Level Circle
    circle_x, circle_y, diameter = 46, 27, 11
    draw.ellipse(
        [circle_x, circle_y, circle_x + diameter, circle_y + diameter],
        outline=(255, 255, 0),
        fill=(0, 0, 0),
    )

    # Draw the static inventory grid
    draw_inventory_borders(draw, GRID_ORIGIN)

    # Static Gold Icon
    gold_icon = get_gold_icon_resized((15, 15))
    canvas.paste(gold_icon, (45, 48), gold_icon)

    return canvas


# Inventory Grid
def create_inventory_grid_image(items: Dict[str, Any]) -> Image.Image:
    """
    Create an image of the inventory grid populated with item icons.
    """
    img = Image.new("RGB", (GRID_W, GRID_H), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    # Draw inner dividers (vertical and horizontal lines)
    for i in range(1, COLS):
        x = i * SLOT_W - PADDING // 2
        draw.line([(x, 0), (x, GRID_H)], fill=(100, 100, 100))
    for j in range(1, ROWS):
        y = j * SLOT_H - PADDING // 2
        draw.line([(0, y), (GRID_W, y)], fill=(100, 100, 100))

    # Paste each item icon into its corresponding slot
    for slot, (col, row) in slot_to_position.items():
        item_name = items.get(slot, {}).get("name", "")
        if item_name and item_name != "empty":
            try:
                icon = brighten_image_cached(
                    get_item_icon_cached(
                        item_name.replace("item_", ""), size=(ITEM_SIZE, ITEM_SIZE)
                    ),
                    1.7,
                )
                x = col * SLOT_W
                y = row * SLOT_H
                img.paste(icon, (x, y))
            except Exception as e:
                print(f"[!] Failed to load item {item_name}: {e}")

    return img


# Main HUD
def create_base_layout(
    hero_name: str,
    level: int,
    hp: float,
    mana: float,
    items: Dict[str, Any],
    kills: int,
    deaths: int,
    assists: int,
    gold: int,
) -> Image.Image:
    """
    Compose the final HUD layout:
      - Renders a static layer (hero portrait, bars, labels, etc.)
      - Overlays dynamic elements like HP/Mana bars, dynamic K/D/A numbers, level, inventory contents, and gold amount.
    """
    # Use cached static layer if available
    static_layer = STATIC_LAYER_CACHE.get(hero_name)
    if not static_layer:
        static_layer = create_static_layer(hero_name)
        STATIC_LAYER_CACHE[hero_name] = static_layer.copy()

    canvas = static_layer.copy()
    draw = ImageDraw.Draw(canvas)

    # Draw dynamic HP and Mana bars
    def draw_bar(
        x: int, y: int, w: int, val: float, color: Tuple[int, int, int]
    ) -> None:
        val = max(0.0, min(1.0, val))
        if int(w * val) > 0:
            draw.rectangle([x, y, x + int(w * val), y + 4], fill=color)

    draw_bar(0, 26, 40, hp, (0, 255, 0))
    draw_bar(0, 32, 40, mana, (0, 100, 255))

    # Render dynamic K/D/A numbers
    for val, y, font9, font8, color in [
        (kills, -2, VERDANA_FONT_9, VERDANA_FONT_8, (0, 255, 0)),
        (deaths, 6, VERDANA_FONT_9, VERDANA_FONT_8, (255, 68, 68)),
        (assists, 14, VERDANA_FONT_9, VERDANA_FONT_8, (128, 248, 255)),
    ]:
        text = str(val)
        font = font8 if val > 9 else font9
        x = 52 if val > 9 else 54
        draw.text((x, y), text, font=font, fill=color)

    # Render the level number inside the level circle
    level_text = str(level)
    font = CONSOLA_FONT_8 if level > 9 else CONSOLA_FONT_10
    circle_x, circle_y, diameter = 47, 27, 10
    bbox = draw.textbbox((0, 0), level_text, font=font)
    tx = circle_x + (diameter - (bbox[2] - bbox[0])) // 2
    ty = circle_y + (diameter - (bbox[3] - bbox[1])) // 2 - (0 if level > 9 else 1)
    draw.text((tx, ty), level_text, font=font, fill=(255, 204, 120))

    # Inventory rendering: use cached inventory grid if possible.
    inventory_data = {slot: items.get(slot, {}) for slot in slot_to_position}
    inventory_key = json.dumps(inventory_data, sort_keys=True)
    global GLOBAL_LAST_INVENTORY_KEY, GLOBAL_CACHED_INVENTORY_IMAGE
    if inventory_key == GLOBAL_LAST_INVENTORY_KEY and GLOBAL_CACHED_INVENTORY_IMAGE:
        inv_grid = GLOBAL_CACHED_INVENTORY_IMAGE
    else:
        inv_grid = create_inventory_grid_image(items)
        GLOBAL_LAST_INVENTORY_KEY = inventory_key
        GLOBAL_CACHED_INVENTORY_IMAGE = inv_grid.copy()

    # Paste the inventory grid into place
    canvas.paste(inv_grid, GRID_ORIGIN)

    # Draw Gold Amount
    gold_text = str(gold)
    offset = {1: 9, 2: 6, 3: 3}.get(len(gold_text), 0)
    draw.text((41 + offset, 40), gold_text, font=CONSOLA_FONT_10, fill=(245, 200, 0))

    return canvas
