"""Asset loader voor GPA Defenders.

Laadt en cached sprites uit spritesheets.
"""

import os
import pygame

# Globale sprite cache
_sprite_cache: dict[str, pygame.Surface] = {}

# Pad naar de assets map
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")

# Mapping: tower_type → (rij, kolom) in de spritesheet
# Rij 0-6, kolom 0-3.  Gesorteerd op kosten (goedkoop → duur).
# Kolom 3 = meest "afgebouwde" versie van elke rij.
TOWER_SPRITE_MAP: dict[str, tuple[int, int]] = {
    "coffee":       (0, 3),   # Rij 1: basis bouwwerk → koffiemachine
    "pen_paper":    (1, 3),   # Rij 2: houten muren → schrijfbureau
    "study_group":  (2, 3),   # Rij 3: versterkt → studieruimte
    "energy_drink": (3, 3),   # Rij 4: met dak → energiecentrale
    "motivatie":    (4, 3),   # Rij 5: kasteel basis → motivatietoren
    "chatgpt":      (5, 3),   # Rij 6: stenen toren → AI-toren
    "tutor":        (6, 3),   # Rij 7: volledig kasteel → tutor-toren
    "hoorcolleges": (6, 1),   # Rij 7 kolom 2: variant → collegezaal
}


def load_spritesheet(path: str, cols: int, rows: int,
                     sprite_w: int = 0, sprite_h: int = 0) -> list[list[pygame.Surface]]:
    """Laad een spritesheet en knip het op in individuele sprites.

    Args:
        path: Pad naar de spritesheet (relatief aan assets/).
        cols: Aantal kolommen in de sheet.
        rows: Aantal rijen in de sheet.
        sprite_w: Breedte per sprite (0 = auto-detect uit sheet).
        sprite_h: Hoogte per sprite (0 = auto-detect uit sheet).

    Returns:
        2D lijst van surfaces [rij][kolom].
    """
    full_path = os.path.join(ASSETS_DIR, path)
    sheet = pygame.image.load(full_path).convert_alpha()

    if sprite_w == 0:
        sprite_w = sheet.get_width() // cols
    if sprite_h == 0:
        sprite_h = sheet.get_height() // rows

    sprites: list[list[pygame.Surface]] = []
    for row in range(rows):
        row_sprites: list[pygame.Surface] = []
        for col in range(cols):
            rect = pygame.Rect(col * sprite_w, row * sprite_h, sprite_w, sprite_h)
            sprite = sheet.subsurface(rect).copy()
            row_sprites.append(sprite)
        sprites.append(row_sprites)

    return sprites


def load_tower_sprites(spritesheet_path: str = "towers/tower_spritesheet.png",
                       cols: int = 4, rows: int = 7) -> dict[str, pygame.Surface]:
    """Laad tower sprites uit de spritesheet en map ze naar tower types.

    Args:
        spritesheet_path: Pad naar de tower spritesheet (relatief aan assets/).
        cols: Aantal kolommen in de sheet.
        rows: Aantal rijen in de sheet.

    Returns:
        Dict van tower_type → pygame.Surface.
    """
    sprites = load_spritesheet(spritesheet_path, cols, rows)

    tower_sprites: dict[str, pygame.Surface] = {}
    for tower_type, (row, col) in TOWER_SPRITE_MAP.items():
        if row < len(sprites) and col < len(sprites[row]):
            tower_sprites[tower_type] = sprites[row][col]

    return tower_sprites


def get_tower_sprite(tower_type: str, size: tuple[int, int] | None = None) -> pygame.Surface | None:
    """Haal een gecachte tower sprite op, geschaald naar de gewenste grootte.

    Args:
        tower_type: Het type toren.
        size: Gewenste (breedte, hoogte). None = originele grootte.

    Returns:
        De sprite surface, of None als niet geladen.
    """
    cache_key = f"tower_{tower_type}_{size}"
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]

    base_key = f"tower_{tower_type}_base"
    base = _sprite_cache.get(base_key)
    if base is None:
        return None

    if size:
        scaled = pygame.transform.smoothscale(base, size)
    else:
        scaled = base

    _sprite_cache[cache_key] = scaled
    return scaled


def init_tower_sprites(spritesheet_path: str = "towers/tower_spritesheet.png",
                       cols: int = 4, rows: int = 7) -> bool:
    """Initialiseer alle tower sprites en sla ze op in de cache.

    Returns:
        True als succesvol geladen, False als het bestand niet gevonden is.
    """
    full_path = os.path.join(ASSETS_DIR, spritesheet_path)
    if not os.path.exists(full_path):
        print(f"[AssetLoader] Spritesheet niet gevonden: {full_path}")
        print("[AssetLoader] Game draait zonder sprites (fallback naar vormen).")
        return False

    tower_sprites = load_tower_sprites(spritesheet_path, cols, rows)
    for tower_type, surface in tower_sprites.items():
        _sprite_cache[f"tower_{tower_type}_base"] = surface

    print(f"[AssetLoader] {len(tower_sprites)} tower sprites geladen.")
    return True


def has_tower_sprites() -> bool:
    """Check of er tower sprites geladen zijn."""
    return any(k.startswith("tower_") for k in _sprite_cache)
