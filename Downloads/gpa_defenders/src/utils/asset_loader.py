"""Asset loader voor GPA Defenders.

Laadt en cached sprites uit losse afbeeldingen (per rij van 4 torens).
Past een kleurtint toe per torentype zodat ze passen bij het schoolthema.
"""

import os
import pygame
from src.settings import TOWER_TYPES

# Globale sprite cache
_sprite_cache: dict[str, pygame.Surface] = {}

# Pad naar de assets map
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")

# Mapping: tower_type → (bestandsnummer 1-7, kolom 0-3)
# Elke afbeelding (tower_1.png t/m tower_7.png) bevat 4 torens naast elkaar.
# Kolom 3 = meest afgebouwde versie.
TOWER_SPRITE_MAP: dict[str, tuple[int, int]] = {
    "coffee":       (1, 3),   # tower_1.png: basis bouwwerk
    "pen_paper":    (2, 3),   # tower_2.png: houten structuur
    "study_group":  (3, 3),   # tower_3.png: versterkt gebouw
    "energy_drink": (4, 3),   # tower_4.png: gebouw met dak
    "motivatie":    (5, 3),   # tower_5.png: kasteel basis
    "chatgpt":      (6, 3),   # tower_6.png: stenen toren
    "tutor":        (7, 3),   # tower_7.png: volledig kasteel
    "hoorcolleges": (7, 1),   # tower_7.png kolom 2: variant
}

# Kleurtint per toren — gebaseerd op de tower color uit settings
# (r, g, b, intensiteit 0-255) — hoe hoger intensiteit, hoe sterker de tint
TOWER_TINTS: dict[str, tuple[int, int, int, int]] = {
    "coffee":       (160, 100, 50, 60),     # warm bruin
    "pen_paper":    (180, 180, 200, 50),     # licht grijs/zilver
    "study_group":  (60, 120, 240, 70),      # blauw
    "energy_drink": (255, 220, 50, 65),      # fel geel
    "motivatie":    (255, 130, 180, 60),      # roze
    "chatgpt":      (90, 230, 220, 65),      # turquoise/teal
    "tutor":        (40, 130, 40, 55),        # donkergroen
    "hoorcolleges": (255, 210, 90, 60),       # goud
}


def _apply_tint(surface: pygame.Surface, tint: tuple[int, int, int, int]) -> pygame.Surface:
    """Pas een kleurtint toe op een sprite.

    Args:
        surface: Originele sprite.
        tint: (r, g, b, intensiteit). Intensiteit 0=geen tint, 255=volledig gekleurd.

    Returns:
        Nieuwe surface met tint.
    """
    r, g, b, intensity = tint
    result = surface.copy()

    # Maak een overlay met de tintkleur
    overlay = pygame.Surface(result.get_size(), pygame.SRCALPHA)
    overlay.fill((r, g, b, intensity))

    # Blend de tint over de sprite (behoudt transparantie van origineel)
    result.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Voeg de kleur-overlay additief toe voor een subtielere tint
    tinted = surface.copy()
    color_layer = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    color_layer.fill((r, g, b, intensity))
    tinted.blit(color_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Mix origineel en getint (50/50) voor een natuurlijk resultaat
    final = surface.copy()
    tinted.set_alpha(intensity)
    final.blit(tinted, (0, 0))

    return final


def _load_row_image(file_num: int, cols: int = 4) -> list[pygame.Surface]:
    """Laad één afbeelding (rij van torens) en knip in kolommen.

    Args:
        file_num: Bestandsnummer (1-7 → tower_1.png t/m tower_7.png).
        cols: Aantal torens naast elkaar in de afbeelding.

    Returns:
        Lijst van sprites (per kolom).
    """
    path = os.path.join(ASSETS_DIR, "towers", f"tower_{file_num}.png")
    img = pygame.image.load(path).convert_alpha()

    sprite_w = img.get_width() // cols
    sprite_h = img.get_height()

    sprites: list[pygame.Surface] = []
    for col in range(cols):
        rect = pygame.Rect(col * sprite_w, 0, sprite_w, sprite_h)
        sprites.append(img.subsurface(rect).copy())

    return sprites


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


def init_tower_sprites() -> bool:
    """Laad alle tower sprites uit losse bestanden en cache ze.

    Verwacht bestanden: assets/towers/tower_1.png t/m tower_7.png
    Elke afbeelding bevat 4 torens naast elkaar.
    Past kleurtint toe per torentype.

    Returns:
        True als succesvol geladen, False als bestanden ontbreken.
    """
    # Check of alle benodigde bestanden bestaan
    needed_files = set(num for num, _ in TOWER_SPRITE_MAP.values())
    for num in needed_files:
        path = os.path.join(ASSETS_DIR, "towers", f"tower_{num}.png")
        if not os.path.exists(path):
            print(f"[AssetLoader] Niet gevonden: {path}")
            print("[AssetLoader] Game draait zonder sprites (fallback naar vormen).")
            return False

    # Laad elke benodigde rij-afbeelding (cache per bestandsnummer)
    row_cache: dict[int, list[pygame.Surface]] = {}
    for num in needed_files:
        row_cache[num] = _load_row_image(num)

    # Map elke tower type naar de juiste sprite met kleurtint
    count = 0
    for tower_type, (file_num, col) in TOWER_SPRITE_MAP.items():
        sprites = row_cache[file_num]
        if col < len(sprites):
            sprite = sprites[col]
            # Pas kleurtint toe als die gedefinieerd is
            tint = TOWER_TINTS.get(tower_type)
            if tint:
                sprite = _apply_tint(sprite, tint)
            _sprite_cache[f"tower_{tower_type}_base"] = sprite
            count += 1

    print(f"[AssetLoader] {count} tower sprites geladen en getint.")
    return True


def has_tower_sprites() -> bool:
    """Check of er tower sprites geladen zijn."""
    return any(k.startswith("tower_") for k in _sprite_cache)


# --------------- Ground tiles ---------------

_grass_tiles: list[pygame.Surface] = []
_path_tiles: list[pygame.Surface] = []

# FieldsTile nummers: 38 = puur gras, 1-37 = puur pad, 39-64 = pad met groen
# We gebruiken 38 voor gras en 1-37 voor pad (de "schoonste" oranje tegels)
_GRASS_TILE_NUMS = [38]
_PATH_TILE_NUMS = list(range(1, 38))


def init_ground_tiles(tile_size: int = 64) -> bool:
    """Laad gras- en padtegels uit FieldsTile_XX.png bestanden.

    Returns:
        True als minstens één tegel geladen is.
    """
    global _grass_tiles, _path_tiles
    _grass_tiles = []
    _path_tiles = []

    tiles_dir = os.path.join(ASSETS_DIR, "tiles")
    if not os.path.isdir(tiles_dir):
        print("[AssetLoader] Tiles map niet gevonden, fallback naar kleuren.")
        return False

    for num in _GRASS_TILE_NUMS:
        path = os.path.join(tiles_dir, f"FieldsTile_{num:02d}.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            _grass_tiles.append(pygame.transform.smoothscale(img, (tile_size, tile_size)))

    for num in _PATH_TILE_NUMS:
        path = os.path.join(tiles_dir, f"FieldsTile_{num:02d}.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            _path_tiles.append(pygame.transform.smoothscale(img, (tile_size, tile_size)))

    loaded = len(_grass_tiles) + len(_path_tiles)
    if loaded:
        print(f"[AssetLoader] {len(_grass_tiles)} gras + {len(_path_tiles)} pad tegels geladen.")
    else:
        print("[AssetLoader] Geen tegels gevonden, fallback naar kleuren.")
    return loaded > 0


def get_grass_tile(index: int) -> pygame.Surface | None:
    """Haal een grastegel op (index voor variatie)."""
    if not _grass_tiles:
        return None
    return _grass_tiles[index % len(_grass_tiles)]


def get_path_tile(index: int) -> pygame.Surface | None:
    """Haal een padtegel op (index voor variatie)."""
    if not _path_tiles:
        return None
    return _path_tiles[index % len(_path_tiles)]


def has_ground_tiles() -> bool:
    """Check of er grondtegels geladen zijn."""
    return bool(_grass_tiles) or bool(_path_tiles)


# --------------- Enemy sprites ---------------

# enemy_type → lijst van animatieframes
_enemy_animations: dict[str, list[pygame.Surface]] = {}

# enemy_type → statisch icon (enkele afbeelding)
_enemy_icons: dict[str, pygame.Surface] = {}

# Animated spritesheets: enemy_type → (bestandsnaam, aantal kolommen)
ENEMY_ANIM_MAP: dict[str, tuple[str, int]] = {
    "professor": ("professor_walk.png", 12),
}

# Statische icons: enemy_type → bestandsnaam
ENEMY_ICON_MAP: dict[str, str] = {
    "quiz":       "quiz.png",
    "huiswerk":   "huiswerk.png",
    "attendance": "attendance.png",
    "opdracht":   "opdracht.png",
    "midterm":    "midterm.png",
    "endterm":    "midterm.png",   # hergebruik exam-icon
}


def init_enemy_sprites(sprite_size: int = 36) -> bool:
    """Laad enemy sprites (animaties en statische icons).

    Verwacht bestanden in assets/enemies/.

    Args:
        sprite_size: Gewenste grootte per frame (vierkant).

    Returns:
        True als minstens één enemy sprite geladen is.
    """
    enemies_dir = os.path.join(ASSETS_DIR, "enemies")
    if not os.path.isdir(enemies_dir):
        return False

    count = 0

    # Laad geanimeerde spritesheets
    for enemy_type, (filename, cols) in ENEMY_ANIM_MAP.items():
        path = os.path.join(enemies_dir, filename)
        if not os.path.exists(path):
            continue

        sheet = pygame.image.load(path).convert_alpha()
        frame_w = sheet.get_width() // cols
        frame_h = sheet.get_height()

        frames: list[pygame.Surface] = []
        for c in range(cols):
            rect = pygame.Rect(c * frame_w, 0, frame_w, frame_h)
            frame = sheet.subsurface(rect).copy()
            frame = pygame.transform.smoothscale(frame, (sprite_size, sprite_size))
            frames.append(frame)

        _enemy_animations[enemy_type] = frames
        count += 1

    # Laad statische icons
    for enemy_type, filename in ENEMY_ICON_MAP.items():
        path = os.path.join(enemies_dir, filename)
        if not os.path.exists(path):
            continue

        img = pygame.image.load(path).convert_alpha()
        _enemy_icons[enemy_type] = pygame.transform.smoothscale(
            img, (sprite_size, sprite_size))
        count += 1

    if count:
        print(f"[AssetLoader] {count} enemy sprite(s) geladen.")
    return count > 0


def get_enemy_frame(enemy_type: str, anim_time: float,
                    fps: float = 10.0) -> pygame.Surface | None:
    """Haal het huidige animatieframe of statisch icon op.

    Args:
        enemy_type: Type vijand.
        anim_time: Tijd in seconden (voor animatie frame-selectie).
        fps: Animatiesnelheid in frames per seconde.

    Returns:
        Het juiste sprite frame, of None als geen sprite beschikbaar.
    """
    # Probeer eerst animatie
    frames = _enemy_animations.get(enemy_type)
    if frames:
        idx = int(anim_time * fps) % len(frames)
        return frames[idx]

    # Anders statisch icon
    return _enemy_icons.get(enemy_type)


def has_enemy_sprites(enemy_type: str) -> bool:
    """Check of een enemy type sprites heeft."""
    return enemy_type in _enemy_animations or enemy_type in _enemy_icons
