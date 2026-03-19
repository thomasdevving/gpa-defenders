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


# ── Game over scherm ──────────────────────────────────────────────────────────

def show_game_over_screen(screen: pygame.Surface, clock: pygame.time.Clock,
                          waves: int, final_gpa: float) -> bool:
    """Toon het game over scherm.

    Returns:
        True  → opnieuw spelen.
        False → afsluiten.
    """
    cx = SCREEN_WIDTH // 2

    font_big   = pygame.font.SysFont(None, 110, bold=True)
    font_sub   = pygame.font.SysFont(None, 36,  bold=True)
    font_stat  = pygame.font.SysFont(None, 30)
    font_btn   = pygame.font.SysFont(None, 34,  bold=True)
    font_small = pygame.font.SysFont(None, 22)

    bw, bh = 260, 58
    btn_retry = pygame.Rect(cx - bw - 16, 530, bw, bh)
    btn_quit  = pygame.Rect(cx + 16,      530, bw, bh)

    # Statistieken
    gpa_kleur = (80, 200, 80) if final_gpa >= 7.0 else (255, 200, 50) if final_gpa >= 5.5 else RED
    stats = [
        ("Waves overleefd",  str(waves),         YELLOW),
        ("Eind GPA",         f"{final_gpa:.1f}", gpa_kleur),
    ]

    # Animatievariabelen
    tick = 0
    # Vallende diploma-snippers (x, y, snelheid, rotatie, rot_snelheid, kleur)
    import random
    rng = random.Random(42)
    snippers = [
        (rng.randint(0, SCREEN_WIDTH),
         rng.randint(-SCREEN_HEIGHT, 0),
         rng.uniform(60, 140),
         rng.uniform(0, 360),
         rng.uniform(-90, 90),
         rng.choice([(220, 50, 50), (180, 30, 30), (255, 80, 80), (140, 20, 20)]))
        for _ in range(28)
    ]

    while True:
        dt = clock.tick(60) / 1000.0
        tick += dt
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_retry.collidepoint(mx, my):
                    return True
                if btn_quit.collidepoint(mx, my):
                    return False

        # ── Achtergrond ──────────────────────────────────────────────────────
        screen.fill((18, 10, 10))
        # Rode gloed in het midden
        for r in range(280, 0, -20):
            alpha = max(0, 38 - r // 8)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (180, 20, 20, alpha), (r, r), r)
            screen.blit(s, (cx - r, SCREEN_HEIGHT // 2 - r))

        # Vallende rode snippers (gesimplificeerd als rechthoekjes)
        for i, (sx, sy, spd, rot, rspd, sc) in enumerate(snippers):
            ny = (sy + spd * tick) % (SCREEN_HEIGHT + 40)
            nr = (rot + rspd * tick) % 360
            snippers[i] = (sx, sy, spd, rot, rspd, sc)
            # Teken als klein rechthoekje (rotatie simuleren met breedte)
            w = max(2, int(8 * abs(math.cos(math.radians(nr)))))
            pygame.draw.rect(screen, sc, (int(sx), int(ny), w, 10))

        # ── Titel ─────────────────────────────────────────────────────────────
        shake = int(2 * math.sin(tick * 18)) if tick < 1.5 else 0
        _outlined(screen, font_big, "GEZAKT!",
                  cx + shake, 80, RED, (60, 0, 0), thick=5)

        sub = font_sub.render("Je GPA is niet gehaald.", True, (200, 160, 160))
        screen.blit(sub, (cx - sub.get_width() // 2, 195))

        # ── Statistieken paneel ───────────────────────────────────────────────
        panel = pygame.Rect(cx - 200, 250, 400, 120)
        pygame.draw.rect(screen, (35, 18, 18), panel, border_radius=10)
        pygame.draw.rect(screen, (100, 40, 40), panel, 2, border_radius=10)

        for i, (label, waarde, kleur) in enumerate(stats):
            y = panel.y + 18 + i * 48
            lbl_s = font_stat.render(label, True, (160, 130, 130))
            val_s = font_stat.render(waarde, True, kleur)
            screen.blit(lbl_s, (panel.x + 24, y))
            screen.blit(val_s, (panel.right - val_s.get_width() - 24, y))
            if i < len(stats) - 1:
                pygame.draw.line(screen, (70, 30, 30),
                                 (panel.x + 16, y + 36), (panel.right - 16, y + 36), 1)

        # ── Knoppen ───────────────────────────────────────────────────────────
        for rect, label, is_retry in [
            (btn_retry, "Opnieuw spelen", True),
            (btn_quit,  "Afsluiten",      False),
        ]:
            hov = rect.collidepoint(mx, my)
            if is_retry:
                bg  = (45, 105, 45) if hov else (30, 75, 30)
                bdr = (80, 170, 80)
            else:
                bg  = (110, 30, 30) if hov else (75, 20, 20)
                bdr = (190, 60, 60)
            pygame.draw.rect(screen, bg,  rect, border_radius=8)
            pygame.draw.rect(screen, bdr, rect, 2, border_radius=8)
            ls = font_btn.render(label, True, WHITE)
            screen.blit(ls, (rect.centerx - ls.get_width() // 2,
                             rect.centery - ls.get_height() // 2))

        hint = font_small.render("ENTER om opnieuw te spelen  •  ESC om af te sluiten",
                                 True, (90, 60, 60))
        screen.blit(hint, (cx - hint.get_width() // 2, btn_retry.bottom + 14))

        pygame.display.flip()


# ── Pauzemenu ─────────────────────────────────────────────────────────────────

def show_pause_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    """Toon het pauzemenu over het huidige spelscherm.

    Returns:
        'continue' → doorgaan.
        'menu'     → terug naar hoofdmenu.
        'quit'     → afsluiten.
    """
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    font_title = pygame.font.SysFont(None, 62, bold=True)
    font_btn   = pygame.font.SysFont(None, 34)

    bw, bh = 280, 56
    gap = 12
    btn_continue = pygame.Rect(cx - bw // 2, cy - 10,                  bw, bh)
    btn_menu     = pygame.Rect(cx - bw // 2, cy - 10 + (bh + gap),     bw, bh)
    btn_quit     = pygame.Rect(cx - bw // 2, cy - 10 + (bh + gap) * 2, bw, bh)

    frozen = screen.copy()

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'continue'
                if event.key == pygame.K_RETURN:
                    return 'continue'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_continue.collidepoint(mx, my):
                    return 'continue'
                if btn_menu.collidepoint(mx, my):
                    return 'menu'
                if btn_quit.collidepoint(mx, my):
                    return 'quit'

        screen.blit(frozen, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        screen.blit(overlay, (0, 0))

        # Paneel (groter voor drie knoppen)
        panel = pygame.Rect(cx - 185, cy - 105, 370, 310)
        pygame.draw.rect(screen, (38, 35, 30), panel, border_radius=12)
        pygame.draw.rect(screen, (100, 90, 75), panel, 3, border_radius=12)

        _outlined(screen, font_title, "GEPAUZEERD", cx, cy - 95, WHITE, (20, 15, 10), thick=2)

        for rect, label, stijl in [
            (btn_continue, "Doorgaan",        'groen'),
            (btn_menu,     "Terug naar menu", 'blauw'),
            (btn_quit,     "Stoppen",         'rood'),
        ]:
            hovered = rect.collidepoint(mx, my)
            if stijl == 'groen':
                bg, border = ((55, 110, 55) if hovered else (38, 82, 38)), (90, 170, 90)
            elif stijl == 'blauw':
                bg, border = ((45, 85, 145) if hovered else (30, 60, 110)), (80, 130, 210)
            else:
                bg, border = ((175, 45, 45) if hovered else (130, 30, 30)), (220, 80, 80)
            pygame.draw.rect(screen, bg,     rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, 2, border_radius=8)
            lbl = font_btn.render(label, True, WHITE)
            screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                               rect.centery - lbl.get_height() // 2))

        hint_font = pygame.font.SysFont(None, 22)
        hint = hint_font.render("ESC of ENTER om door te gaan", True, (140, 130, 115))
        screen.blit(hint, (cx - hint.get_width() // 2, btn_quit.bottom + 14))

        pygame.display.flip()


# ── Modusselectiescherm ───────────────────────────────────────────────────────

def _draw_mode_bg(screen: pygame.Surface, font_title: pygame.font.Font,
                  cx: int, font_small: pygame.font.Font) -> None:
    screen.fill((22, 26, 38))
    for gx in range(0, SCREEN_WIDTH, 48):
        pygame.draw.line(screen, (30, 35, 50), (gx, 0), (gx, SCREEN_HEIGHT), 1)
    for gy in range(0, SCREEN_HEIGHT, 48):
        pygame.draw.line(screen, (30, 35, 50), (0, gy), (SCREEN_WIDTH, gy), 1)
    _outlined(screen, font_title, "Hoe wil je spelen?",
              cx, 38, WHITE, (10, 12, 22), thick=2)
    pygame.draw.line(screen, (55, 62, 90), (40, 100), (SCREEN_WIDTH - 40, 100), 1)
    hint = font_small.render("Klik op een kaart  |  ESC om terug te gaan",
                             True, (70, 80, 110))
    screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_HEIGHT - 22))


def _draw_mode_card(screen: pygame.Surface, card: pygame.Rect, titel: str,
                    kleur: tuple, regels: list, badge: str,
                    font_head: pygame.font.Font, font_body: pygame.font.Font,
                    font_small: pygame.font.Font, hov: bool) -> None:
    bg = (38, 46, 66) if hov else (28, 34, 50)
    bc = kleur if hov else (52, 62, 92)
    pygame.draw.rect(screen, bg, card, border_radius=12)
    pygame.draw.rect(screen, kleur, (card.x, card.y, card.width, 6), border_radius=4)
    pygame.draw.rect(screen, bc, card, 2, border_radius=12)

    th = font_head.render(titel, True, kleur)
    screen.blit(th, (card.centerx - th.get_width() // 2, card.y + 18))

    bf = font_small.render(badge, True, (22, 26, 38))
    bpad = 8
    br = pygame.Rect(card.right - bf.get_width() - bpad * 2 - 8,
                     card.y + 16, bf.get_width() + bpad * 2, 20)
    pygame.draw.rect(screen, kleur, br, border_radius=4)
    screen.blit(bf, (br.x + bpad, br.y + 2))

    for i, regel in enumerate(regels):
        if not regel:
            continue
        col = kleur if regel.endswith(":") else (
            (155, 165, 185) if any(c in regel for c in (":", "Pijl", "Numpad", "Muis"))
            else (188, 196, 218))
        rs = font_body.render(regel, True, col)
        screen.blit(rs, (card.x + 20, card.y + 58 + i * 30))


def show_mode_select_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    """Toon het scherm om singleplayer, local co-op of online te kiezen.

    Returns:
        'single' → singleplayer.
        'multi'  → local co-op.
        'online' → online co-op (ga naar lobby).
        'back'   → terug naar startscherm.
    """
    cx = SCREEN_WIDTH // 2

    font_title = pygame.font.SysFont(None, 56, bold=True)
    font_head  = pygame.font.SysFont(None, 30, bold=True)
    font_body  = pygame.font.SysFont(None, 22)
    font_small = pygame.font.SysFont(None, 21)

    # 3 kaarten naast elkaar
    card_w, card_h, gap = 290, 360, 18
    total = 3 * card_w + 2 * gap
    x0 = cx - total // 2
    card_y = 108
    cards = [
        pygame.Rect(x0,                   card_y, card_w, card_h),
        pygame.Rect(x0 + card_w + gap,    card_y, card_w, card_h),
        pygame.Rect(x0 + (card_w + gap)*2, card_y, card_w, card_h),
    ]

    defs = [
        ("Singleplayer", (255, 210, 60), "1 speler", 'single', [
            "Speel alleen.",
            "",
            "Muis: toren plaatsen",
            "1-4: toren selecteren",
            "SPACE: volgende wave",
            "ESC: pauze",
        ]),
        ("Local Co-op", (80, 200, 255), "2 spelers", 'multi', [
            "Samen op 1 scherm.",
            "",
            "Speler 1: muis",
            "",
            "Speler 2:",
            "Pijltjes: cursor",
            "Numpad 1-4: toren",
            "Numpad 0: plaatsen",
        ]),
        ("Online Co-op", (100, 220, 120), "via netwerk", 'online', [
            "Samen via internet",
            "of lokaal netwerk.",
            "",
            "Host: start server,",
            "deel je IP-adres.",
            "",
            "Join: voer het IP",
            "van de host in.",
        ]),
    ]

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'back'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 'back'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for card, (_, _, _, result, _) in zip(cards, defs):
                    if card.collidepoint(mx, my):
                        return result

        _draw_mode_bg(screen, font_title, cx, font_small)
        for card, (titel, kleur, badge, _, regels) in zip(cards, defs):
            _draw_mode_card(screen, card, titel, kleur, regels, badge,
                            font_head, font_body, font_small,
                            card.collidepoint(mx, my))
        pygame.display.flip()


# ── Online lobby ──────────────────────────────────────────────────────────────

def show_network_lobby_screen(screen: pygame.Surface,
                              clock: pygame.time.Clock):
    """Lobby-scherm: kies Host of Join en maak verbinding.

    Returns:
        (NetworkClient, is_host: bool) bij succes.
        None bij annuleren.
    """
    from src.network.client import NetworkClient
    from src.network.server import GameServer, get_local_ip

    cx = SCREEN_WIDTH // 2

    font_title = pygame.font.SysFont(None, 52, bold=True)
    font_head  = pygame.font.SysFont(None, 32, bold=True)
    font_body  = pygame.font.SysFont(None, 26)
    font_small = pygame.font.SysFont(None, 22)
    font_mono  = pygame.font.SysFont("monospace", 26)

    bw, bh = 220, 52
    btn_host = pygame.Rect(cx - bw - 16, 190, bw, bh)
    btn_join = pygame.Rect(cx + 16,      190, bw, bh)
    btn_back = pygame.Rect(cx - 90,      SCREEN_HEIGHT - 68, 180, 44)

    # Toestand
    mode      = None      # 'host' of 'join'
    status    = ""
    error     = ""
    ip_input  = ""        # tekstveld voor join-IP
    server    = None
    client    = None
    waiting   = False

    local_ip = get_local_ip()

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if server:
                    server.stop()
                if client:
                    client.disconnect()
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if server:
                        server.stop()
                    if client:
                        client.disconnect()
                    return None

                # Tekstveld voor IP-invoer
                if mode == 'join' and not waiting:
                    if event.key == pygame.K_BACKSPACE:
                        ip_input = ip_input[:-1]
                    elif event.key == pygame.K_RETURN and ip_input:
                        # Verbinden
                        client = NetworkClient()
                        status = f"Verbinden met {ip_input}..."
                        error  = ""
                        waiting = True
                        if client.connect(ip_input):
                            status = "Verbonden! Wachten op host..."
                        else:
                            error   = "Verbinding mislukt. Controleer het IP."
                            status  = ""
                            client  = None
                            waiting = False
                    elif len(ip_input) < 15:
                        ch = event.unicode
                        if ch in "0123456789.":
                            ip_input += ch

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mx, my):
                    if server:
                        server.stop()
                    if client:
                        client.disconnect()
                    return None

                if mode is None:
                    if btn_host.collidepoint(mx, my):
                        mode   = 'host'
                        server = GameServer()
                        server.start()
                        client = NetworkClient()
                        client.connect("127.0.0.1")
                        status = f"Server gestart  |  Jouw IP: {local_ip}"
                        waiting = True
                    elif btn_join.collidepoint(mx, my):
                        mode   = 'join'
                        status = "Voer het IP-adres van de host in:"

        # Controleer of het spel is gestart (gezet door recv-thread)
        if client and client.game_started:
            return client, (mode == 'host')

        # ── Tekenen ──────────────────────────────────────────────────────────
        screen.fill((22, 26, 38))
        for gx in range(0, SCREEN_WIDTH, 48):
            pygame.draw.line(screen, (30, 35, 50), (gx, 0), (gx, SCREEN_HEIGHT), 1)
        for gy in range(0, SCREEN_HEIGHT, 48):
            pygame.draw.line(screen, (30, 35, 50), (0, gy), (SCREEN_WIDTH, gy), 1)

        _outlined(screen, font_title, "Online Co-op",
                  cx, 38, WHITE, (10, 12, 22), thick=2)
        pygame.draw.line(screen, (55, 62, 90), (40, 100), (SCREEN_WIDTH - 40, 100), 1)

        if mode is None:
            # Host / Join knoppen
            sub = font_body.render("Kies hoe je wilt verbinden:", True, (160, 170, 195))
            screen.blit(sub, (cx - sub.get_width() // 2, 148))

            for btn, label, kleur in [
                (btn_host, "Host game",  (100, 220, 120)),
                (btn_join, "Join game",  (80,  190, 255)),
            ]:
                hov = btn.collidepoint(mx, my)
                bg  = tuple(min(255, c + 25) for c in kleur) if hov else tuple(c // 2 for c in kleur)
                pygame.draw.rect(screen, bg,    btn, border_radius=8)
                pygame.draw.rect(screen, kleur, btn, 2, border_radius=8)
                ls = font_head.render(label, True, WHITE)
                screen.blit(ls, (btn.centerx - ls.get_width() // 2,
                                 btn.centery - ls.get_height() // 2))

            info = font_small.render(
                "Host: start een server en deel je IP.   Join: voer IP van host in.",
                True, (90, 100, 130))
            screen.blit(info, (cx - info.get_width() // 2, 270))

        elif mode == 'host':
            # Wachten op tweede speler
            ts = font_head.render("Wachten op speler 2...", True, (100, 220, 120))
            screen.blit(ts, (cx - ts.get_width() // 2, 165))

            ip_lbl = font_body.render("Deel dit IP-adres met je medespeler:", True, (160, 170, 195))
            screen.blit(ip_lbl, (cx - ip_lbl.get_width() // 2, 230))

            ip_box = pygame.Rect(cx - 160, 268, 320, 46)
            pygame.draw.rect(screen, (35, 42, 60), ip_box, border_radius=8)
            pygame.draw.rect(screen, (100, 220, 120), ip_box, 2, border_radius=8)
            ip_s = font_mono.render(local_ip, True, (100, 220, 120))
            screen.blit(ip_s, (ip_box.centerx - ip_s.get_width() // 2,
                               ip_box.centery - ip_s.get_height() // 2))

            port_s = font_small.render(f"Poort: 5555", True, (90, 100, 130))
            screen.blit(port_s, (cx - port_s.get_width() // 2, 326))

        elif mode == 'join':
            ts = font_head.render("Verbinden met host", True, (80, 190, 255))
            screen.blit(ts, (cx - ts.get_width() // 2, 165))

            if not waiting:
                lbl = font_body.render("IP-adres van de host:", True, (160, 170, 195))
                screen.blit(lbl, (cx - lbl.get_width() // 2, 222))

                inp_box = pygame.Rect(cx - 160, 256, 320, 46)
                pygame.draw.rect(screen, (35, 42, 60), inp_box, border_radius=8)
                pygame.draw.rect(screen, (80, 190, 255), inp_box, 2, border_radius=8)
                disp = ip_input + ("|" if (pygame.time.get_ticks() // 500) % 2 == 0 else "")
                ip_s = font_mono.render(disp or " ", True, WHITE)
                screen.blit(ip_s, (inp_box.x + 12,
                                   inp_box.centery - ip_s.get_height() // 2))

                hint2 = font_small.render("ENTER om te verbinden", True, (90, 100, 130))
                screen.blit(hint2, (cx - hint2.get_width() // 2, 314))
            else:
                ws = font_body.render("Verbonden! Wachten op host...", True, (80, 190, 255))
                screen.blit(ws, (cx - ws.get_width() // 2, 256))

        # Status / fout
        if status:
            ss = font_small.render(status, True, (130, 190, 130))
            screen.blit(ss, (cx - ss.get_width() // 2, 380))
        if error:
            es = font_small.render(error, True, RED)
            screen.blit(es, (cx - es.get_width() // 2, 380))

        # Terug-knop
        hov = btn_back.collidepoint(mx, my)
        pygame.draw.rect(screen, (65, 35, 35) if hov else (45, 22, 22),
                         btn_back, border_radius=8)
        pygame.draw.rect(screen, (180, 60, 60), btn_back, 2, border_radius=8)
        bl = font_body.render("Terug", True, WHITE)
        screen.blit(bl, (btn_back.centerx - bl.get_width() // 2,
                         btn_back.centery - bl.get_height() // 2))

        pygame.display.flip()


# ── Tutorial scherm ───────────────────────────────────────────────────────────

def show_tutorial_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> bool:
    """Toon het uitlegscherm voor het spel begint.

    Returns:
        True  → speler wil starten.
        False → speler sluit het venster.
    """
    cx = SCREEN_WIDTH // 2

    font_title = pygame.font.SysFont(None, 52, bold=True)
    font_head  = pygame.font.SysFont(None, 30, bold=True)
    font_body  = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 21)

    bw, bh = 240, 56
    btn = pygame.Rect(cx - bw // 2, SCREEN_HEIGHT - 72, bw, bh)

    # ── Inhoud ────────────────────────────────────────────────────────────────
    secties = [
        {
            "titel": "Doel van het spel",
            "kleur": (255, 220, 60),
            "regels": [
                "Vijanden lopen over een pad richting jouw GPA.",
                "Als ze het einde bereiken, daalt je GPA.",
                "Zakt je GPA onder de 5,5? Dan ben je GEZAKT.",
                "Overleef zoveel mogelijk waves!",
            ],
        },
        {
            "titel": "Torens plaatsen",
            "kleur": (100, 200, 100),
            "regels": [
                "Klik op een groene grastegel om een toren te plaatsen.",
                "Je betaalt met Energy, verdiend door vijanden te verslaan.",
                "Selecteer een toren via de kaarten onderaan of toets 1 t/m 4.",
                "Je kunt geen torens op het pad plaatsen.",
            ],
        },
        {
            "titel": "Vijanden",
            "kleur": (255, 120, 80),
            "regels": [
                "Quiz: zwak, langzaam, weinig GPA-schade.",
                "Huiswerk: snel en gevaarlijker.",
                "Midterm/Endterm: veel HP, traag maar zware GPA-schade.",
                "Professor: eindbaas met enorm HP en maximale schade.",
            ],
        },
        {
            "titel": "Torens",
            "kleur": (120, 180, 255),
            "regels": [
                "Koffie (5 ECTS): snel vuren, lage schade.",
                "Studiegroep (10 ECTS): vertraagt vijanden.",
                "Tutor (20 ECTS): hoge schade, traag vuren.",
                "Energy Drink (15 ECTS): extreem snel vuren.",
            ],
        },
    ]

    # Verdeel 4 secties in 2 kolommen × 2 rijen
    COL_W    = SCREEN_WIDTH // 2 - 40
    ROW_H    = 168
    CARD_X   = [30, SCREEN_WIDTH // 2 + 10]
    CARD_Y   = [118, 118 + ROW_H + 12]

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        btn_hov = btn.collidepoint(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn.collidepoint(mx, my):
                    return True

        # ── Achtergrond ──────────────────────────────────────────────────────
        screen.fill((22, 26, 38))
        # Subtiele rasterlijnen
        for gx in range(0, SCREEN_WIDTH, 48):
            pygame.draw.line(screen, (30, 35, 50), (gx, 0), (gx, SCREEN_HEIGHT), 1)
        for gy in range(0, SCREEN_HEIGHT, 48):
            pygame.draw.line(screen, (30, 35, 50), (0, gy), (SCREEN_WIDTH, gy), 1)

        # ── Koptitel ─────────────────────────────────────────────────────────
        _outlined(screen, font_title, "Hoe werkt het?",
                  cx, 28, WHITE, (10, 12, 22), thick=2)

        # Scheidingslijn
        pygame.draw.line(screen, (60, 68, 95),
                         (30, 98), (SCREEN_WIDTH - 30, 98), 1)

        # ── Sectiekaarten ─────────────────────────────────────────────────────
        for idx, sectie in enumerate(secties):
            col = idx % 2
            row = idx // 2
            cx_card = CARD_X[col]
            cy_card = CARD_Y[row]

            card_rect = pygame.Rect(cx_card, cy_card, COL_W, ROW_H)

            # Kaart achtergrond
            pygame.draw.rect(screen, (32, 38, 55), card_rect, border_radius=10)
            # Gekleurde linkerrand
            pygame.draw.rect(screen, sectie["kleur"],
                             (cx_card, cy_card, 4, ROW_H), border_radius=2)
            pygame.draw.rect(screen, (52, 60, 85), card_rect, 1, border_radius=10)

            # Sectie titel
            th = font_head.render(sectie["titel"], True, sectie["kleur"])
            screen.blit(th, (cx_card + 14, cy_card + 10))

            # Regels
            for i, regel in enumerate(sectie["regels"]):
                # Bullet
                bul_x = cx_card + 14
                bul_y = cy_card + 42 + i * 26 + 8
                pygame.draw.circle(screen, sectie["kleur"], (bul_x, bul_y), 3)
                rs = font_body.render(regel, True, (188, 195, 215))
                screen.blit(rs, (bul_x + 10, cy_card + 42 + i * 26))

        # ── Startknop ────────────────────────────────────────────────────────
        bg_btn = (55, 115, 55) if btn_hov else (38, 85, 38)
        pygame.draw.rect(screen, bg_btn, btn, border_radius=10)
        pygame.draw.rect(screen, (90, 175, 90), btn, 2, border_radius=10)
        lbl = font_head.render("Spel starten", True, WHITE)
        screen.blit(lbl, (btn.centerx - lbl.get_width() // 2,
                          btn.centery - lbl.get_height() // 2))

        # Hint
        hint = font_small.render("ENTER of SPACE om te starten  •  ESC om terug te gaan",
                                 True, (90, 98, 125))
        screen.blit(hint, (cx - hint.get_width() // 2, SCREEN_HEIGHT - 18))

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
