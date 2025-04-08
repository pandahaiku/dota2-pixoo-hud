import json
import logging
from PIL import Image, ImageDraw, ImageFont
from dota_2_cdn import (
    get_hero_portrait_cached,
    get_item_icon_cached,
    brighten_image_cached,
    get_gold_icon_resized,
)


class HUDRenderer:
    def __init__(self):
        # Caches for static layers and inventory images
        self.static_layer_cache = {}
        self.last_inventory_key = None
        self.cached_inventory_image = None

        # Layout constants for inventory grid
        self.ITEM_SIZE = 12  # Target size for item icons
        self.PADDING = 2  # Extra spacing added to each slot
        self.COLS = 3  # Number of columns in the inventory grid
        self.ROWS = 2  # Number of rows in the inventory grid
        self.SLOT_W = self.ITEM_SIZE - 1 + self.PADDING
        self.SLOT_H = self.ITEM_SIZE - 1 + self.PADDING
        self.GRID_W = self.COLS * self.SLOT_W - self.PADDING
        self.GRID_H = self.ROWS * self.SLOT_H - self.PADDING
        self.GRID_ORIGIN = (2, 39)  # Top-left point where the inventory grid is drawn
        self.slot_to_position = {
            "slot0": (0, 0),
            "slot1": (1, 0),
            "slot2": (2, 0),
            "slot3": (0, 1),
            "slot4": (1, 1),
            "slot5": (2, 1),
        }

        # Load fonts
        self.CONSOLA_FONT_10 = self.load_font("consola.ttf", 10)
        self.CONSOLA_FONT_9 = self.load_font("consola.ttf", 9)
        self.CONSOLA_FONT_8 = self.load_font("consola.ttf", 8)
        self.VERDANA_FONT_9 = self.load_font("verdana.ttf", 9)
        self.VERDANA_FONT_8 = self.load_font("verdana.ttf", 8)

    def load_font(self, path: str, size: int) -> ImageFont.FreeTypeFont:
        """Attempt to load a TrueType font, with a fallback to the default."""
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            logging.warning(f"Could not load font '{path}'. Falling back to default.")
            return ImageFont.load_default()

    def draw_inventory_borders(self, draw: ImageDraw.Draw, origin: tuple) -> None:
        inv_x, inv_y = origin
        # Fill the inventory area with a dark gray background
        draw.rectangle(
            [inv_x - 1, inv_y - 1, inv_x + self.GRID_W, inv_y + self.GRID_H],
            fill=(30, 30, 30),
        )
        # Draw left/right vertical borders
        for i in range(2):
            draw.line(
                [(inv_x - 2 + i, inv_y - 1), (inv_x - 2 + i, inv_y + self.GRID_H)],
                fill=(100, 100, 100),
            )
            draw.line(
                [
                    (inv_x + self.GRID_W + i, inv_y - 1),
                    (inv_x + self.GRID_W + i, inv_y + self.GRID_H),
                ],
                fill=(100, 100, 100),
            )
        # Draw top and bottom horizontal borders
        draw.line(
            [(inv_x - 2, inv_y - 1), (inv_x + self.GRID_W + 1, inv_y - 1)],
            fill=(100, 100, 100),
        )
        draw.line(
            [
                (inv_x - 2, inv_y + self.GRID_H),
                (inv_x + self.GRID_W + 1, inv_y + self.GRID_H),
            ],
            fill=(100, 100, 100),
        )
        # Draw inner grid dividers
        for i in range(1, self.COLS):
            x = inv_x + i * self.SLOT_W - self.PADDING // 2
            draw.line([(x, inv_y), (x, inv_y + self.GRID_H)], fill=(100, 100, 100))
        for j in range(1, self.ROWS):
            y = inv_y + j * self.SLOT_H - self.PADDING // 2
            draw.line([(inv_x, y), (inv_x + self.GRID_W, y)], fill=(100, 100, 100))

    def create_static_layer(self, hero_name: str) -> Image.Image:
        canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 255))
        draw = ImageDraw.Draw(canvas)

        # Add hero portrait with brightness enhancement
        portrait = brighten_image_cached(get_hero_portrait_cached(hero_name), 1.3)
        canvas.paste(portrait, (0, 0))

        # Draw HP and Mana bar backgrounds
        draw.rectangle([0, 26, 40, 30], fill=(50, 50, 50))
        draw.rectangle([0, 32, 40, 36], fill=(50, 50, 50))

        # Draw static K/D/A labels
        kda_x = 43
        draw.text((kda_x, 0), "K", font=self.CONSOLA_FONT_10, fill=(0, 255, 0))
        draw.text((48, -2), ":", font=self.VERDANA_FONT_9, fill=(0, 255, 0))
        draw.text((kda_x, 8), "D", font=self.CONSOLA_FONT_10, fill=(255, 68, 68))
        draw.text((48, 6), ":", font=self.VERDANA_FONT_9, fill=(255, 68, 68))
        draw.text((kda_x, 16), "A", font=self.CONSOLA_FONT_10, fill=(128, 248, 255))
        draw.text((48, 14), ":", font=self.VERDANA_FONT_9, fill=(128, 248, 255))

        # Static level circle
        circle_x, circle_y, diameter = 46, 27, 11
        draw.ellipse(
            [circle_x, circle_y, circle_x + diameter, circle_y + diameter],
            outline=(255, 255, 0),
            fill=(0, 0, 0),
        )

        # Draw the inventory grid borders
        self.draw_inventory_borders(draw, self.GRID_ORIGIN)

        # Static Gold Icon
        gold_icon = get_gold_icon_resized((15, 15))
        canvas.paste(gold_icon, (45, 48), gold_icon)

        return canvas

    def create_inventory_grid_image(self, items: dict) -> Image.Image:
        img = Image.new("RGB", (self.GRID_W, self.GRID_H), (30, 30, 30))
        draw = ImageDraw.Draw(img)

        # Draw inner grid lines
        for i in range(1, self.COLS):
            x = i * self.SLOT_W - self.PADDING // 2
            draw.line([(x, 0), (x, self.GRID_H)], fill=(100, 100, 100))
        for j in range(1, self.ROWS):
            y = j * self.SLOT_H - self.PADDING // 2
            draw.line([(0, y), (self.GRID_W, y)], fill=(100, 100, 100))

        # Paste item icons into grid slots
        for slot, (col, row) in self.slot_to_position.items():
            item_name = items.get(slot, {}).get("name", "")
            if item_name and item_name != "empty":
                try:
                    icon = brighten_image_cached(
                        get_item_icon_cached(
                            item_name.replace("item_", ""),
                            size=(self.ITEM_SIZE, self.ITEM_SIZE),
                        ),
                        1.7,
                    )
                    x = col * self.SLOT_W
                    y = row * self.SLOT_H
                    img.paste(icon, (x, y))
                except Exception as e:
                    logging.error(f"[!] Failed to load item {item_name}: {e}")
        return img

    def create_base_layout(
        self,
        hero_name: str,
        level: int,
        hp: float,
        mana: float,
        items: dict,
        kills: int,
        deaths: int,
        assists: int,
        gold: int,
    ) -> Image.Image:
        # Use cached static layer if available
        if hero_name in self.static_layer_cache:
            static_layer = self.static_layer_cache[hero_name].copy()
        else:
            static_layer = self.create_static_layer(hero_name)
            self.static_layer_cache[hero_name] = static_layer.copy()

        canvas = static_layer.copy()
        draw = ImageDraw.Draw(canvas)

        # Draw dynamic HP and Mana bars
        def draw_bar(x: int, y: int, w: int, val: float, color: tuple) -> None:
            val = max(0.0, min(1.0, val))
            if int(w * val) > 0:
                draw.rectangle([x, y, x + int(w * val), y + 4], fill=color)

        draw_bar(0, 26, 40, hp, (0, 255, 0))
        draw_bar(0, 32, 40, mana, (0, 100, 255))

        # Render dynamic K/D/A numbers
        for val, y, font9, font8, color in [
            (kills, -2, self.VERDANA_FONT_9, self.VERDANA_FONT_8, (0, 255, 0)),
            (deaths, 6, self.VERDANA_FONT_9, self.VERDANA_FONT_8, (255, 68, 68)),
            (assists, 14, self.VERDANA_FONT_9, self.VERDANA_FONT_8, (128, 248, 255)),
        ]:
            text = str(val)
            font = font8 if val > 9 else font9
            x = 52 if val > 9 else 54
            draw.text((x, y), text, font=font, fill=color)

        # Render the level number inside the level circle
        level_text = str(level)
        font = self.CONSOLA_FONT_8 if level > 9 else self.CONSOLA_FONT_10
        circle_x, circle_y, diameter = 47, 27, 10
        bbox = draw.textbbox((0, 0), level_text, font=font)
        tx = circle_x + (diameter - (bbox[2] - bbox[0])) // 2
        ty = circle_y + (diameter - (bbox[3] - bbox[1])) // 2 - (0 if level > 9 else 1)
        draw.text((tx, ty), level_text, font=font, fill=(255, 204, 120))

        # Inventory rendering: cache the grid if unchanged
        inventory_data = {slot: items.get(slot, {}) for slot in self.slot_to_position}
        inventory_key = json.dumps(inventory_data, sort_keys=True)
        if (
            inventory_key == self.last_inventory_key
            and self.cached_inventory_image is not None
        ):
            inv_grid = self.cached_inventory_image
        else:
            inv_grid = self.create_inventory_grid_image(items)
            self.last_inventory_key = inventory_key
            self.cached_inventory_image = inv_grid.copy()

        # Paste the inventory grid
        canvas.paste(inv_grid, self.GRID_ORIGIN)

        # Draw Gold Amount
        gold_text = str(gold)
        offset = {1: 9, 2: 6, 3: 3}.get(len(gold_text), 0)
        draw.text(
            (41 + offset, 40), gold_text, font=self.CONSOLA_FONT_10, fill=(245, 200, 0)
        )

        return canvas
