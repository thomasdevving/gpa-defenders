"""UI schermen voor GPA Defenders."""

import math
import pygame
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, GREEN, RED

# ── Kleurenpalet ──────────────────────────────────────────────────────────────
_SKY_TOP   = (82,  165, 222)
_SKY_BOT   = (162, 212, 248)
_CLOUD     = (242, 248, 255)
_MTN       = (142, 152, 162)
_MTN_SNOW  = (228, 236, 248)
_HILL      = (72,  142, 52)
_HILL_D    = (52,  112, 38)
_GROUND    = (88,  158, 62)
_GROUND_D  = (62,  118, 42)
_PATH      = (192, 162, 112)
_TREE_G    = (48,  128, 42)
_TREE_D    = (28,   88, 28)
_TRUNK     = (102,  70, 40)

_BRICK     = (188,  76,  46)
_BRICK_D   = (145,  50,  26)
_STONE     = (182, 172, 158)
_STONE_D   = (148, 138, 124)
_ROOF_C    = (84,   56,  34)
_WIN_F     = (52,   40,  26)
_WIN_G     = (152, 202, 240)
_DOOR_C    = (102,  68,  36)

_BAN_W     = (152,  96,  40)
_BAN_D     = (98,   56,  16)
_TITLE_O   = (240, 105,  15)
_TITLE_Y   = (255, 195,  35)
_TITLE_SH  = (82,   25,   4)

_BTN_RING  = (192, 186, 175)
_BTN_D     = (125, 118, 108)
_PLAY_C    = (208,  80,  20)
_PLAY_H    = (238, 110,  45)
_PLAY_D    = (130,  45,   6)

_ICON_BG   = (162, 155, 144)
_ICON_H    = (202, 195, 184)
_ICON_D    = (102,  95,  86)


# ── Achtergrond ───────────────────────────────────────────────────────────────

def _sky(surf: pygame.Surface) -> None:
    for y in range(500):
        t = y / 499
        r = int(_SKY_TOP[0] + (_SKY_BOT[0] - _SKY_TOP[0]) * t)
        g = int(_SKY_TOP[1] + (_SKY_BOT[1] - _SKY_TOP[1]) * t)
        b = int(_SKY_TOP[2] + (_SKY_BOT[2] - _SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))


def _cloud(surf: pygame.Surface, x: int, y: int, scale: float = 1.0) -> None:
    r = int(36 * scale)
    pygame.draw.ellipse(surf, _CLOUD, (x - r, y - r // 2, r * 2, r))
    pygame.draw.ellipse(surf, _CLOUD, (x - r // 2, y - r, r, r))
    pygame.draw.ellipse(surf, _CLOUD, (x + r // 4, y - r * 3 // 4, r * 3 // 4, r * 3 // 4))
    pygame.draw.ellipse(surf, _CLOUD, (x - r, y - r // 4, r * 2 + r // 4, r * 3 // 4))


def _mountains(surf: pygame.Surface) -> None:
    peaks = [(120, 285), (275, 195), (415, 255), (565, 158), (705, 212), (855, 182), (975, 238)]
    for px, py in peaks:
        pygame.draw.polygon(surf, _MTN,
                            [(px - 92, 410), (px, py), (px + 92, 410)])
    for px, py in peaks:
        pygame.draw.polygon(surf, _MTN_SNOW,
                            [(px - 20, py + 48), (px, py), (px + 20, py + 48)])


def _hills(surf: pygame.Surface) -> None:
    for rect in [
        (-80, 385, 380, 195), (195, 405, 345, 158),
        (448, 415, 295, 135), (675, 392, 375, 178), (975, 405, 195, 148),
    ]:
        col = _HILL if rect[0] % 2 == 0 else _HILL_D
        pygame.draw.ellipse(surf, _HILL, rect)


def _ground(surf: pygame.Surface) -> None:
    pygame.draw.rect(surf, _GROUND_D, (0, 462, SCREEN_WIDTH, SCREEN_HEIGHT - 462))
    pygame.draw.rect(surf, _GROUND,   (0, 462, SCREEN_WIDTH, 75))
    # Pad van links naar rechts gebouw
    path = [(285, 540), (738, 540), (775, 582), (248, 582)]
    pygame.draw.polygon(surf, _PATH, path)


def _tree(surf: pygame.Surface, x: int, y: int, s: float = 1.0) -> None:
    th, tw = int(28 * s), int(7 * s)
    pygame.draw.rect(surf, _TRUNK, (x - tw // 2, y - th, tw, th))
    r1, r2, r3 = int(20 * s), int(16 * s), int(12 * s)
    pygame.draw.circle(surf, _TREE_D, (x, y - th - r1 + 6), r1)
    pygame.draw.circle(surf, _TREE_G, (x - 4, y - th - r2 - 4), r2)
    pygame.draw.circle(surf, _TREE_G, (x + 5, y - th - r3 - 5), r3)


def _trees(surf: pygame.Surface) -> None:
    for x, y, s in [
        (45, 518, 0.9), (92, 508, 1.1), (138, 522, 0.8),
        (915, 512, 1.0), (962, 502, 1.2), (1008, 518, 0.85),
        (228, 488, 0.75), (788, 486, 0.8), (818, 492, 0.7),
    ]:
        _tree(surf, x, y, s)


def _birds(surf: pygame.Surface, tick: int) -> None:
    for i, (bx, by) in enumerate([(115, 72), (285, 52), (638, 86), (778, 66)]):
        x = int((bx + tick * 0.025 * (i % 2 + 1)) % (SCREEN_WIDTH + 80))
        wing = int(4 * math.sin(tick / 200 + i * 1.5))
        pygame.draw.lines(surf, (32, 42, 68), False,
                          [(x - 10, by - wing), (x, by), (x + 10, by - wing)], 2)


# ── Hulpfuncties tekst ────────────────────────────────────────────────────────

def _outlined(surf: pygame.Surface, font: pygame.font.Font, text: str,
              cx: int, y: int, fg: tuple, shadow: tuple, thick: int = 3) -> None:
    """Tekst met dikke omtrek."""
    for dx in range(-thick, thick + 1):
        for dy in range(-thick, thick + 1):
            if abs(dx) + abs(dy) >= thick:
                s = font.render(text, True, shadow)
                surf.blit(s, (cx - s.get_width() // 2 + dx, y + dy))
    s = font.render(text, True, fg)
    surf.blit(s, (cx - s.get_width() // 2, y))


# ── Titelbanner ───────────────────────────────────────────────────────────────

def _banner(surf: pygame.Surface, font_l: pygame.font.Font, font_s: pygame.font.Font,
            cx: int, y: int) -> None:
    bw, bh = 640, 125
    bx, by = cx - bw // 2, y
    # Drie houten planken
    for i in range(3):
        pygame.draw.rect(surf, _BAN_W, (bx, by + i * 40, bw, 39))
        pygame.draw.rect(surf, _BAN_D, (bx, by + i * 40, bw, 2))
    # Buitenrand
    pygame.draw.rect(surf, _BAN_D, (bx, by, bw, bh), 4)
    # Hoekbouten
    for boltx in (bx + 14, bx + bw - 18):
        for bolty in (by + 14, by + bh - 18):
            pygame.draw.circle(surf, (178, 145, 75), (boltx, bolty), 8)
            pygame.draw.circle(surf, _BAN_D, (boltx, bolty), 8, 2)

    # Titel twee regels: "GPA" boven, "DEFENDERS" onder
    _outlined(surf, font_l, "GPA",       cx, by + 8,  _TITLE_Y, _TITLE_SH, 4)
    _outlined(surf, font_l, "DEFENDERS", cx, by + 58, _TITLE_O, _TITLE_SH, 4)

    # Ondertitel onder banner — met donkere omtrek voor leesbaarheid
    _outlined(surf, font_s, "— Bescherm je diploma! —",
              cx, by + bh + 6, (255, 238, 100), (40, 20, 0), thick=2)


# ── Speelknop ─────────────────────────────────────────────────────────────────

def _play_button(surf: pygame.Surface, cx: int, cy: int,
                 hovered: bool, tick: int) -> None:
    ro, ri = 74, 62
    # Schaduw
    pygame.draw.circle(surf, (22, 18, 14), (cx + 6, cy + 7), ro)
    # Buitenste ring
    pygame.draw.circle(surf, _BTN_D,    (cx, cy), ro)
    pygame.draw.circle(surf, _BTN_RING, (cx, cy), ro - 5)
    # Binnenste cirkel
    pygame.draw.circle(surf, _PLAY_D, (cx, cy), ri + 3)
    pygame.draw.circle(surf, _PLAY_H if hovered else _PLAY_C, (cx, cy), ri)
    # Driehoek (play-icoon)
    tx, ty = cx - 14, cy
    pygame.draw.polygon(surf, WHITE, [(tx, ty - 28), (tx, ty + 28), (tx + 42, ty)])
    pygame.draw.polygon(surf, (215, 195, 175), [(tx, ty - 28), (tx, ty + 28), (tx + 42, ty)], 2)
    # Pulserend randje bij hover
    if hovered:
        pulse = int(3 * math.sin(tick / 140))
        pygame.draw.circle(surf, (255, 218, 95), (cx, cy), ro + pulse, 3)


# ── Raam helper ───────────────────────────────────────────────────────────────

def _window(surf: pygame.Surface, x: int, y: int, w: int = 26, h: int = 30) -> None:
    pygame.draw.rect(surf, _WIN_F, (x, y, w, h))
    pygame.draw.rect(surf, _WIN_G, (x + 2, y + 2, w - 4, h - 4))
    mx, my = x + w // 2, y + h // 2
    pygame.draw.line(surf, _WIN_F, (mx, y + 2), (mx, y + h - 2), 2)
    pygame.draw.line(surf, _WIN_F, (x + 2, my), (x + w - 2, my), 2)
    pygame.draw.line(surf, (215, 238, 255), (x + 3, y + 3), (x + 6, y + 7), 1)


# ── Schoolgebouw links: Basisschool met trapgevel en klokkentoren ─────────────

def _school_left(surf: pygame.Surface, cx: int, base: int) -> None:
    bw, bh = 158, 148
    bx, by = cx - bw // 2, base - bh

    # Hoofdmuur
    pygame.draw.rect(surf, _BRICK, (bx, by, bw, bh))
    for row in range(0, bh, 13):
        pygame.draw.line(surf, _BRICK_D, (bx, by + row), (bx + bw, by + row), 1)

    # Trapgevel (stepped gable) — typisch Nederlandse school
    gable = [
        (bx, by), (bx + bw, by),
        (bx + bw, by - 12), (bx + bw - 22, by - 12),
        (bx + bw - 22, by - 32), (bx + bw - 44, by - 32),
        (bx + bw - 44, by - 52), (cx + 12, by - 52),
        (cx + 12, by - 72), (cx - 12, by - 72),
        (cx - 12, by - 52), (bx + 44, by - 52),
        (bx + 44, by - 32), (bx + 22, by - 32),
        (bx + 22, by - 12), (bx, by - 12),
    ]
    pygame.draw.polygon(surf, _BRICK, gable)
    pygame.draw.polygon(surf, _BRICK_D, gable, 3)

    # Naambordje boven ingang
    pygame.draw.rect(surf, (218, 198, 148), (bx + 32, by - 4, bw - 64, 20))
    pygame.draw.rect(surf, _BAN_D, (bx + 32, by - 4, bw - 64, 20), 2)
    lf = pygame.font.SysFont(None, 16)
    lb = lf.render("BASISSCHOOL", True, (58, 38, 18))
    surf.blit(lb, (cx - lb.get_width() // 2, by))

    # Ramen: 2 rijen × 3 kolommen
    for row in range(2):
        for col in range(3):
            _window(surf, bx + 14 + col * 44, by + 20 + row * 58)

    # Deur met boog
    dx, dy = cx - 18, base - 52
    pygame.draw.rect(surf, _WIN_F, (dx, dy, 36, 52))
    pygame.draw.rect(surf, _DOOR_C, (dx + 2, dy + 2, 32, 48))
    pygame.draw.circle(surf, YELLOW, (dx + 28, dy + 26), 3)
    pygame.draw.arc(surf, _WIN_F, pygame.Rect(dx, dy - 10, 36, 20), 0, math.pi, 4)

    # Klokkentoren boven trapgevel
    tx, tw, th = cx - 20, 40, 58
    ty = by - 72 - th
    pygame.draw.rect(surf, _BRICK_D, (tx, ty, tw, th))
    # Klok-raam (rond)
    pygame.draw.circle(surf, _WIN_F, (cx, ty + 22), 11)
    pygame.draw.circle(surf, _WIN_G, (cx, ty + 22), 9)
    pygame.draw.line(surf, _WIN_F, (cx, ty + 13), (cx, ty + 31), 2)
    pygame.draw.line(surf, _WIN_F, (cx - 9, ty + 22), (cx + 9, ty + 22), 2)
    # Puntdak toren
    roof_pts = [(tx - 6, ty), (tx + tw + 6, ty), (cx, ty - 32)]
    pygame.draw.polygon(surf, _ROOF_C, roof_pts)
    pygame.draw.polygon(surf, _BAN_D, roof_pts, 2)
    # Vlag
    pygame.draw.line(surf, (115, 85, 48), (cx, ty - 32), (cx, ty - 68), 2)
    pygame.draw.polygon(surf, RED,
                        [(cx, ty - 68), (cx + 24, ty - 59), (cx, ty - 50)])

    # Struikjes
    for sx in [bx - 6, bx + 16, bx + bw - 20, bx + bw + 4]:
        pygame.draw.circle(surf, _TREE_G, (sx, base - 6), 15)
        pygame.draw.circle(surf, _TREE_D, (sx, base - 6), 15, 2)


# ── Schoolgebouw rechts: UvA Science Park ─────────────────────────────────────

# UvA Science Park kleuren
_CONC      = (208, 204, 196)   # beton/gevelbekleding
_CONC_D    = (172, 168, 158)
_CONC_L    = (228, 225, 218)
_GLASS_M   = (118, 168, 205)   # glasgevel midden
_GLASS_L   = (158, 205, 235)   # glasgevel licht (reflectie)
_GLASS_D   = (78,  128, 165)   # glasgevel donker
_FRAME_C   = (182, 178, 172)   # aluminium kozijnen
_COL_W     = (222, 220, 216)   # witte draagkolommen
_UVA_P     = (92,  44,  148)   # UvA paars
_UVA_PD    = (62,  26,  108)   # UvA paars donker
_DOME_S    = (175, 178, 182)   # koepel zilver
_DOME_SD   = (132, 135, 140)


def _uva_x(surf: pygame.Surface, cx: int, cy: int, size: int) -> None:
    """Teken het Amsterdam Andreaskruis (drie X'en gestapeld)."""
    s = size
    for dy_off in (-s, 0, s):
        y = cy + dy_off
        pygame.draw.line(surf, (220, 215, 230), (cx - s, y - s + 2), (cx + s, y + s - 2), 2)
        pygame.draw.line(surf, (220, 215, 230), (cx + s, y - s + 2), (cx - s, y + s - 2), 2)


def _school_right(surf: pygame.Surface, cx: int, base: int) -> None:
    """UvA Science Park: modern glasgebouw op pilaren + paarse silo's."""
    bw = 185
    bx = cx - bw // 2

    # ── 1. Plat achtergebouw (parkeergarage/faculteitsgebouw) ─────────────────
    fb_x  = bx - 48
    fb_w  = 105
    fb_h  = 82
    fb_y  = base - fb_h
    # Horizontale betonbanden (kenmerkend voor het gebouw)
    band_h = 11
    for i in range(fb_h // band_h + 1):
        col = _CONC if i % 2 == 0 else _CONC_D
        pygame.draw.rect(surf, col, (fb_x, fb_y + i * band_h, fb_w, band_h))
    pygame.draw.rect(surf, _CONC_D, (fb_x, fb_y, fb_w, fb_h), 2)
    # Kleine strooksramen
    for row in range(3):
        pygame.draw.rect(surf, _GLASS_D,
                         (fb_x + 6, fb_y + 10 + row * 24, fb_w - 12, 9))

    # ── 2. Paarse silo's (cilindrisch, UvA logo) ──────────────────────────────
    silo_defs = [
        (cx - 20, base - 188, 38, 95),   # links, iets lager
        (cx + 14, base - 205, 34, 112),  # rechts, hoger en smaller
    ]
    for sx, sy_top, sw, sh in silo_defs:
        # Schaduw
        pygame.draw.rect(surf, (40, 20, 70), (sx - sw // 2 + 3, sy_top + 4, sw, sh))
        # Body
        pygame.draw.rect(surf, _UVA_PD, (sx - sw // 2, sy_top, sw, sh))
        pygame.draw.rect(surf, _UVA_P,  (sx - sw // 2 + 1, sy_top, sw - 2, sh - 1))
        # Lichte rand links (cylinder ronding suggestie)
        pygame.draw.line(surf, (128, 78, 188),
                         (sx - sw // 2 + 3, sy_top + 4),
                         (sx - sw // 2 + 3, sy_top + sh - 4), 2)
        # Amsterdam X-kruis logo (midden van de silo)
        _uva_x(surf, sx, sy_top + sh // 2, sw // 2 - 4)
        # Zilveren koepel
        dr = sw // 2 + 5
        pygame.draw.ellipse(surf, _DOME_SD, (sx - dr, sy_top - 14, dr * 2, 20))
        pygame.draw.ellipse(surf, _DOME_S,  (sx - dr, sy_top - 16, dr * 2, 20))
        # Koepelrand
        pygame.draw.rect(surf, _DOME_SD,   (sx - sw // 2 - 2, sy_top - 4, sw + 4, 6))
        # Antenne
        pygame.draw.line(surf, _DOME_SD, (sx, sy_top - 16), (sx, sy_top - 30), 1)
        pygame.draw.circle(surf, _DOME_SD, (sx, sy_top - 30), 2)

    # ── 3. Glazen hoofdgebouw (elevated op kolommen) ──────────────────────────
    gb_h  = 118
    gb_y  = base - 28 - gb_h   # 28px vrije ruimte voor kolommen

    # Betonnen buitenframe
    pygame.draw.rect(surf, _CONC_D, (bx - 7, gb_y - 5, bw + 14, gb_h + 10))
    pygame.draw.rect(surf, _CONC,   (bx - 5, gb_y - 3, bw + 10, gb_h + 6))

    # Glasgevel (6 kolommen × 4 rijen)
    cols_n, rows_n = 6, 4
    cw = bw // cols_n
    rh = gb_h // rows_n
    glass_palette = [_GLASS_L, _GLASS_M, _GLASS_D, _GLASS_M, _GLASS_L, _GLASS_D]
    for row in range(rows_n):
        for col in range(cols_n):
            wx = bx + col * cw + 2
            wy = gb_y + row * rh + 2
            gc = glass_palette[col]
            # Lichte reflectiestreep bovenaan elk raam
            pygame.draw.rect(surf, gc,      (wx, wy, cw - 4, rh - 4))
            pygame.draw.rect(surf, _GLASS_L, (wx + 1, wy + 1, cw - 6, 4))
    # Aluminium kozijnen (horizontaal)
    for row in range(rows_n + 1):
        pygame.draw.line(surf, _FRAME_C,
                         (bx, gb_y + row * rh), (bx + bw, gb_y + row * rh), 2)
    # Aluminium kozijnen (verticaal)
    for col in range(cols_n + 1):
        pygame.draw.line(surf, _FRAME_C,
                         (bx + col * cw, gb_y), (bx + col * cw, gb_y + gb_h), 2)

    # Betonnen onderbalk (overhang)
    pygame.draw.rect(surf, _CONC_D, (bx - 10, gb_y + gb_h + 3, bw + 20, 7))

    # ── 4. Draagkolommen (witte ronde pijlers) ────────────────────────────────
    n_col  = 7
    col_w  = 7
    col_h  = 28
    for i in range(n_col):
        px = bx + 6 + i * (bw - 12) // (n_col - 1)
        pygame.draw.rect(surf, _CONC_D, (px - col_w // 2, base - col_h, col_w, col_h))
        pygame.draw.rect(surf, _COL_W,  (px - col_w // 2 + 1, base - col_h, col_w - 2, col_h - 1))

    # ── 5. Naambordje op gebouw ───────────────────────────────────────────────
    lf = pygame.font.SysFont(None, 15)
    lb = lf.render("UvA Science Park", True, _CONC_L)
    surf.blit(lb, (cx - lb.get_width() // 2, gb_y + 4))

    # ── 6. Vlaggenmasten voor het gebouw ──────────────────────────────────────
    for fx in [bx + 20, bx + bw - 20]:
        pygame.draw.line(surf, _CONC_D, (fx, base - 5), (fx, base - 55), 2)
        # Nederlandse vlag (rood-wit-blauw)
        for fi, fc in enumerate([(RED, 0), ((240, 240, 240), 6), ((42, 82, 160), 12)]):
            pygame.draw.rect(surf, fc[0], (fx + 2, base - 55 + fi * 6, 18, 6))

    # ── 7. Gras en fietsenstalling ────────────────────────────────────────────
    # Klein fietsenstalling-hekje
    pygame.draw.rect(surf, _CONC_D, (bx - 30, base - 18, 22, 3))
    for hx in range(bx - 28, bx - 8, 5):
        pygame.draw.line(surf, _CONC_D, (hx, base - 18), (hx, base - 6), 1)
    # Struikjes
    for sx in [bx - 8, bx + bw + 6]:
        pygame.draw.circle(surf, _TREE_G, (sx, base - 7), 13)
        pygame.draw.circle(surf, _TREE_D, (sx, base - 7), 13, 2)


# ── Besturing-legenda ─────────────────────────────────────────────────────────

def _controls(surf: pygame.Surface, font: pygame.font.Font, cx: int, y: int) -> None:
    hints = [
        ("SPACE", "wave starten"),
        ("1–4", "toren kiezen"),
        ("klik", "toren plaatsen"),
        ("ESC", "stoppen"),
    ]
    # Meet de breedte van elk item voor correcte verdeling
    badge_w = 58
    gap = 8
    items = []
    for key, desc in hints:
        k_surf = font.render(key, True, YELLOW)
        d_surf = font.render(desc, True, (195, 185, 170))
        item_w = badge_w + gap + d_surf.get_width()
        items.append((key, desc, k_surf, d_surf, item_w))

    spacing = 18  # vaste tussenruimte tussen items
    total_w = sum(w for *_, w in items) + spacing * (len(items) - 1)
    x0 = cx - total_w // 2

    x = x0
    for key, desc, k_surf, d_surf, item_w in items:
        pygame.draw.rect(surf, (55, 50, 44), (x, y, badge_w, 22), border_radius=4)
        pygame.draw.rect(surf, (118, 108, 95), (x, y, badge_w, 22), 2, border_radius=4)
        surf.blit(k_surf, (x + badge_w // 2 - k_surf.get_width() // 2, y + 3))
        surf.blit(d_surf, (x + badge_w + gap, y + 3))
        x += item_w + spacing


# ── Pauzemenu ─────────────────────────────────────────────────────────────────

def show_pause_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> bool:
    """Toon het pauzemenu over het huidige spelscherm.

    Returns:
        True  → doorgaan.
        False → stoppen.
    """
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    font_title = pygame.font.SysFont(None, 62, bold=True)
    font_btn   = pygame.font.SysFont(None, 36)

    bw, bh = 280, 60
    btn_continue = pygame.Rect(cx - bw // 2, cy - 10,      bw, bh)
    btn_quit     = pygame.Rect(cx - bw // 2, cy + bh + 16, bw, bh)

    # Vries het huidige scherm in als achtergrond
    frozen = screen.copy()

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True          # ESC nogmaals = doorgaan
                if event.key == pygame.K_RETURN:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_continue.collidepoint(mx, my):
                    return True
                if btn_quit.collidepoint(mx, my):
                    return False

        # Bevroren spelscherm als achtergrond
        screen.blit(frozen, (0, 0))

        # Semi-transparante overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        screen.blit(overlay, (0, 0))

        # Paneel
        panel = pygame.Rect(cx - 175, cy - 90, 350, 260)
        pygame.draw.rect(screen, (38, 35, 30), panel, border_radius=12)
        pygame.draw.rect(screen, (100, 90, 75), panel, 3, border_radius=12)

        # Titel
        _outlined(screen, font_title, "GEPAUZEERD", cx, cy - 80, WHITE, (20, 15, 10), thick=2)

        # Knoppen
        for rect, label, is_quit in [
            (btn_continue, "Doorgaan",  False),
            (btn_quit,     "Stoppen",   True),
        ]:
            hovered = rect.collidepoint(mx, my)
            if is_quit:
                bg     = (175, 45, 45) if hovered else (130, 30, 30)
                border = (220, 80, 80)
            else:
                bg     = (55, 110, 55) if hovered else (38, 82, 38)
                border = (90, 170, 90)
            pygame.draw.rect(screen, bg,     rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)
            lbl = font_btn.render(label, True, WHITE)
            screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                               rect.centery - lbl.get_height() // 2))

        # Hint
        hint_font = pygame.font.SysFont(None, 22)
        hint = hint_font.render("ESC of ENTER om door te gaan", True, (140, 130, 115))
        screen.blit(hint, (cx - hint.get_width() // 2, btn_quit.bottom + 14))

        pygame.display.flip()


# ── Hoofd startscherm ─────────────────────────────────────────────────────────

def show_start_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> bool:
    """Toon het startscherm.

    Returns:
        True  → speler wil starten.
        False → speler sluit het venster.
    """
    cx = SCREEN_WIDTH // 2

    font_title = pygame.font.SysFont(None, 82, bold=True)
    font_sub   = pygame.font.SysFont(None, 30, bold=True)
    font_info  = pygame.font.SysFont(None, 22)

    play_cx, play_cy, play_r = cx, 462, 72

    # Wolken: vaste y-posities, variabele x-startposities
    cloud_defs = [(75, 68, 1.2), (295, 52, 0.9), (548, 82, 1.4), (798, 60, 1.0)]

    tick = 0

    while True:
        dt = clock.tick(60)
        tick += dt

        mx, my = pygame.mouse.get_pos()
        play_hovered = (mx - play_cx) ** 2 + (my - play_cy) ** 2 <= play_r ** 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_hovered:
                    return True

        # ── Achtergrond ──────────────────────────────────────────────────────
        _sky(screen)
        _mountains(screen)

        # Wolken bewegen langzaam naar rechts
        for i, (bx, by, scale) in enumerate(cloud_defs):
            x = int((bx + tick * 0.022 * (i % 2 + 1)) % (SCREEN_WIDTH + 160)) - 80
            _cloud(screen, x, by, scale)

        _hills(screen)
        _ground(screen)
        _trees(screen)
        _birds(screen, tick)

        # ── Schoolgebouwen ───────────────────────────────────────────────────
        _school_left(screen, 182, 572)
        _school_right(screen, 842, 572)

        # ── Titelbanner ──────────────────────────────────────────────────────
        _banner(screen, font_title, font_sub, cx, 28)

        # ── Speelknop ────────────────────────────────────────────────────────
        _play_button(screen, play_cx, play_cy, play_hovered, tick)

        # Hint onder speelknop
        hint = font_info.render("ENTER  of  klik om te spelen", True, (205, 195, 178))
        screen.blit(hint, (cx - hint.get_width() // 2, play_cy + play_r + 12))

        # ── Besturing onderaan ───────────────────────────────────────────────
        _controls(screen, font_info, cx, 682)

        pygame.display.flip()
