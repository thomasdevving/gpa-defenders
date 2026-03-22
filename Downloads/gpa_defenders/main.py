"""GPA Defenders - Main entry point.

Start het spel door dit bestand te runnen:
    python main.py
"""

import math
import pygame
from src.network.client import NetworkClient
from src.ui.screens import (show_start_screen, show_pause_menu, show_tutorial_screen,
                            show_game_over_screen, show_mode_select_screen,
                            show_network_lobby_screen)
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    GRASS_COLOR, PATH_COLOR, WHITE, RED, GREEN, YELLOW, GRAY,
    TOWER_TYPES,
)
from src.managers.grid import GridMap
from src.managers.wave_manager import WaveManager
from src.managers.game_manager import GameManager
from src.utils.asset_loader import (
    init_tower_sprites, init_ground_tiles, init_enemy_sprites,
    get_grass_tile, get_path_tile, has_ground_tiles,
)


def draw_tower_icon(screen: pygame.Surface, tower_type: str,
                    cx: int, cy: int, sz: int, active: bool = True) -> None:
    """Teken het hand-getekende icoon voor een torentype.

    Wordt gebruikt in zowel het menu als op geplaatste torens.
    """
    col = TOWER_TYPES[tower_type]["color"] if active else (68, 65, 60)

    if tower_type == "coffee":
        hw = int(sz * 0.52)
        pts = [(cx - hw, cy - int(sz * 0.08)),
               (cx + hw, cy - int(sz * 0.08)),
               (cx + int(hw * 0.72), cy + int(sz * 0.5)),
               (cx - int(hw * 0.72), cy + int(sz * 0.5))]
        pygame.draw.polygon(screen, col, pts)
        pygame.draw.polygon(screen, (40, 25, 10), pts, 2)
        pygame.draw.arc(screen, col,
                        pygame.Rect(cx + int(hw * 0.58), cy, int(hw * 0.7), int(sz * 0.32)),
                        -math.pi * 0.5, math.pi * 0.5, 3)
        sc = (185, 188, 205) if active else (70, 68, 65)
        for ox in (-int(sz * 0.2), 0, int(sz * 0.2)):
            for k in range(2):
                y1 = cy - int(sz * 0.18) - k * 7
                pygame.draw.line(screen, sc,
                                 (cx + ox, y1),
                                 (cx + ox + ((-1) ** k) * 4, y1 - 5), 2)

    elif tower_type == "study_group":
        skin = (200, 168, 128) if active else (68, 65, 60)
        for ox in (-int(sz * 0.28), int(sz * 0.28)):
            pygame.draw.circle(screen, skin,
                               (cx + ox, cy - int(sz * 0.24)), int(sz * 0.17))
            pygame.draw.line(screen, col,
                             (cx + ox, cy - int(sz * 0.06)),
                             (cx + ox, cy + int(sz * 0.32)), 3)
            pygame.draw.line(screen, col,
                             (cx + ox - int(sz * 0.18), cy + int(sz * 0.1)),
                             (cx + ox + int(sz * 0.18), cy + int(sz * 0.1)), 2)

    elif tower_type == "tutor":
        hw, hh = int(sz * 0.46), int(sz * 0.36)
        page1 = (228, 222, 208) if active else (72, 70, 65)
        page2 = (244, 240, 226) if active else (78, 75, 70)
        lc = (148, 138, 122) if active else (58, 56, 52)
        pygame.draw.rect(screen, page1, (cx - hw, cy - hh, hw, hh * 2))
        pygame.draw.rect(screen, page2, (cx,      cy - hh, hw, hh * 2))
        pygame.draw.line(screen, col, (cx, cy - hh), (cx, cy + hh), 2)
        for k in range(4):
            y = cy - hh + 7 + k * max(1, (hh * 2 - 14) // 4)
            pygame.draw.line(screen, lc, (cx - hw + 5, y), (cx - 4, y), 1)
            pygame.draw.line(screen, lc, (cx + 4,      y), (cx + hw - 5, y), 1)

    elif tower_type == "energy_drink":
        # Bliksemflits
        pts = [
            (cx + int(sz * 0.08),  cy - int(sz * 0.48)),
            (cx - int(sz * 0.22),  cy + int(sz * 0.05)),
            (cx + int(sz * 0.05),  cy + int(sz * 0.05)),
            (cx - int(sz * 0.08),  cy + int(sz * 0.48)),
            (cx + int(sz * 0.28),  cy - int(sz * 0.05)),
            (cx - int(sz * 0.05),  cy - int(sz * 0.05)),
        ]
        pygame.draw.polygon(screen, col, pts)
        if active:
            pygame.draw.polygon(screen, (255, 160, 30), pts, 2)

    elif tower_type == "chatgpt":
        # Chatbubbel met "AI"
        bw, bh = int(sz * 0.7), int(sz * 0.5)
        pygame.draw.ellipse(screen, col, (cx - bw, cy - bh, bw * 2, bh * 2))
        # Driehoekje onderaan bubbel
        pygame.draw.polygon(screen, col, [
            (cx - int(sz * 0.15), cy + bh - 2),
            (cx + int(sz * 0.1), cy + bh - 2),
            (cx - int(sz * 0.25), cy + bh + int(sz * 0.2)),
        ])
        outline = (50, 180, 170) if active else (55, 52, 48)
        pygame.draw.ellipse(screen, outline, (cx - bw, cy - bh, bw * 2, bh * 2), 2)
        # "AI" tekst
        font = pygame.font.SysFont(None, max(12, int(sz * 0.55)), bold=True)
        txt = font.render("AI", True, (255, 255, 255) if active else (90, 88, 82))
        screen.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

    elif tower_type == "pen_paper":
        # Pen diagonaal over een papiertje
        pw, ph = int(sz * 0.4), int(sz * 0.5)
        paper = (230, 225, 210) if active else (72, 70, 65)
        pygame.draw.rect(screen, paper, (cx - pw, cy - ph, pw * 2, ph * 2), border_radius=2)
        pygame.draw.rect(screen, col, (cx - pw, cy - ph, pw * 2, ph * 2), 2, border_radius=2)
        # Lijntjes op papier
        lc = (148, 138, 122) if active else (58, 56, 52)
        for k in range(4):
            ly = cy - ph + int(ph * 0.35) + k * max(1, int(ph * 0.35))
            pygame.draw.line(screen, lc, (cx - pw + 4, ly), (cx + pw - 4, ly), 1)
        # Pen (diagonaal)
        pen_col = (100, 100, 120) if active else (55, 52, 48)
        pygame.draw.line(screen, pen_col,
                         (cx + int(sz * 0.15), cy - int(sz * 0.4)),
                         (cx - int(sz * 0.2), cy + int(sz * 0.35)), 3)
        # Penpunt
        pygame.draw.circle(screen, (220, 180, 50) if active else (60, 55, 45),
                           (cx - int(sz * 0.2), cy + int(sz * 0.35)), 2)

    elif tower_type == "motivatie":
        # Vlam / vuur (motivatie-energie)
        flame = col
        # Buitenste vlam
        pts_outer = [
            (cx, cy - int(sz * 0.5)),
            (cx + int(sz * 0.3), cy + int(sz * 0.1)),
            (cx + int(sz * 0.2), cy + int(sz * 0.45)),
            (cx - int(sz * 0.2), cy + int(sz * 0.45)),
            (cx - int(sz * 0.3), cy + int(sz * 0.1)),
        ]
        pygame.draw.polygon(screen, flame, pts_outer)
        # Binnenste vlam (lichter)
        inner = (255, 200, 100) if active else (80, 75, 68)
        pts_inner = [
            (cx, cy - int(sz * 0.2)),
            (cx + int(sz * 0.13), cy + int(sz * 0.15)),
            (cx + int(sz * 0.1), cy + int(sz * 0.4)),
            (cx - int(sz * 0.1), cy + int(sz * 0.4)),
            (cx - int(sz * 0.13), cy + int(sz * 0.15)),
        ]
        pygame.draw.polygon(screen, inner, pts_inner)

    elif tower_type == "hoorcolleges":
        # Megafoon / luidspreker
        # Trechter
        pts = [
            (cx - int(sz * 0.15), cy - int(sz * 0.15)),
            (cx + int(sz * 0.45), cy - int(sz * 0.4)),
            (cx + int(sz * 0.45), cy + int(sz * 0.4)),
            (cx - int(sz * 0.15), cy + int(sz * 0.15)),
        ]
        pygame.draw.polygon(screen, col, pts)
        pygame.draw.polygon(screen, (180, 150, 50) if active else (55, 52, 48), pts, 2)
        # Handvat
        pygame.draw.rect(screen, col,
                         (cx - int(sz * 0.35), cy - int(sz * 0.12),
                          int(sz * 0.22), int(sz * 0.24)), border_radius=2)
        # Geluidsgolven
        wave_col = (255, 230, 130) if active else (65, 62, 55)
        for k in range(1, 3):
            r = int(sz * 0.2) + k * int(sz * 0.12)
            pygame.draw.arc(screen, wave_col,
                            pygame.Rect(cx + int(sz * 0.3), cy - r, r * 2, r * 2),
                            -0.6, 0.6, 2)


class Game:
    """Hoofdclass die de game loop beheert.

    Attributes:
        screen: Het pygame scherm.
        clock: Pygame clock voor FPS.
        grid_map: Beheert map, pad en plaatsingsregels.
        wave_manager: Beheert wave opbouw en status.
        game_manager: Beheert combat, resources en game over.
        selected_tower: Huidig geselecteerd torentype.
    """

    def __init__(self, screen: pygame.Surface = None, clock: pygame.time.Clock = None,
                 multiplayer: bool = False,
                 network_client: "NetworkClient | None" = None,
                 is_host: bool = False):
        if not pygame.get_init():
            pygame.init()
        if screen is None:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(TITLE)
        else:
            self.screen = screen
        self.clock = clock if clock is not None else pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)

        self.grid_map = GridMap()
        self.wave_manager = WaveManager(
            self.grid_map.waypoints,
            wave_pressure_multiplier=self.grid_map.wave_pressure_multiplier,
        )
        self.game_manager = GameManager()
        init_tower_sprites()
        init_ground_tiles(TILE_SIZE)
        init_enemy_sprites()

        self.selected_tower_type = "coffee"
        self.tower_types_list = list(TOWER_TYPES.keys())
        self.pause_btn = pygame.Rect(8, 8, 38, 38)
        self._setup_tower_cards()

        # Netwerk (online multiplayer)
        self.net: NetworkClient | None = network_client
        self.is_host = is_host

        # Geselecteerde toren (voor verkoop/upgrade-UI)
        self.selected_tower = None
        self._sell_btn: pygame.Rect | None = None
        self._upgrade_btns: dict[str, pygame.Rect] = {}
        self._perk_card_rects: list[tuple[str, pygame.Rect]] = []

        # Snelheidsknop (rechtsboven, naast pauzeknop)
        self.speed_btn = pygame.Rect(SCREEN_WIDTH - 90, 8, 80, 38)

        # Automatische wave-countdown
        self._wave_countdown: float = 5.0   # initieel 5s voor eerste wave
        self._was_wave_active: bool = False  # vorige frame state

        # Speler 2
        self.multiplayer = multiplayer or (network_client is not None)
        if self.multiplayer and network_client is None:
            # Lokale co-op cursor
            self.p2_gx = GRID_COLS // 2
            self.p2_gy = GRID_ROWS // 2
            self.p2_tower_type = "coffee"

    def _setup_tower_cards(self) -> None:
        """Bereken de klikbare kaart-rects voor torenselectie (2 rijen van 4)."""
        ui_y = GRID_ROWS * TILE_SIZE
        ui_h = SCREEN_HEIGHT - ui_y
        cols = 4
        card_w, gap = 110, 10
        row_gap = 8
        pad_top = 8
        card_h = (ui_h - pad_top * 2 - row_gap) // 2

        # Beschikbare ruimte rechts van het info-paneel
        info_w = 270
        avail_w = SCREEN_WIDTH - info_w - 20
        total_w = cols * card_w + (cols - 1) * gap
        x0 = info_w + (avail_w - total_w) // 2

        self.tower_cards: dict[str, pygame.Rect] = {}
        for i, t in enumerate(self.tower_types_list):
            row = i // cols
            col = i % cols
            x = x0 + col * (card_w + gap)
            y = ui_y + pad_top + row * (card_h + row_gap)
            self.tower_cards[t] = pygame.Rect(x, y, card_w, card_h)

    def _draw_tower_icon(self, tower_type: str, cx: int, cy: int,
                         sz: int, active: bool) -> None:
        """Teken het icoon voor een torentype (altijd hand-getekend)."""
        draw_tower_icon(self.screen, tower_type, cx, cy, sz, active)

    def _draw_tower_cards(self, ui_y: int) -> None:
        """Teken de klikbare torenselectiekaarten."""
        mx, my = pygame.mouse.get_pos()
        rects = list(self.tower_cards.values())

        # Houten tray achter de kaarten (omvat beide rijen)
        pad = 8
        tray = pygame.Rect(
            rects[0].x - pad - 6,
            rects[0].y - pad,
            max(r.right for r in rects) - rects[0].x + (pad + 6) * 2,
            max(r.bottom for r in rects) - rects[0].y + pad * 2,
        )
        plank_h = tray.height // 3 + 1
        for i in range(3):
            c = (108, 70, 30) if i % 2 == 0 else (88, 55, 20)
            pygame.draw.rect(self.screen, c,
                             (tray.x, tray.y + i * (tray.height // 3), tray.width, plank_h))
        pygame.draw.rect(self.screen, (58, 36, 10), tray, 3)
        # Bouten
        for bx in (tray.x + 8, tray.right - 10):
            for by in (tray.y + 8, tray.bottom - 10):
                pygame.draw.circle(self.screen, (178, 148, 72), (bx, by), 5)
                pygame.draw.circle(self.screen, (95, 72, 28), (bx, by), 5, 1)

        num_font = pygame.font.SysFont(None, 19, bold=True)
        name_font = pygame.font.SysFont(None, 19)
        cost_font = pygame.font.SysFont(None, 19, bold=True)

        for i, (tower_type, rect) in enumerate(self.tower_cards.items()):
            config = TOWER_TYPES[tower_type]
            is_sel = tower_type == self.selected_tower_type
            can_afford = self.game_manager.energy >= config["cost"]
            hovered = rect.collidepoint(mx, my) and not is_sel and can_afford

            # Achtergrond
            if is_sel:
                bg = (92, 70, 32)
            elif not can_afford:
                bg = (38, 34, 30)
            elif hovered:
                bg = (74, 57, 26)
            else:
                bg = (55, 42, 20)
            pygame.draw.rect(self.screen, bg, rect, border_radius=8)

            # Rand
            if is_sel:
                bc, bw = (228, 202, 98), 3
            elif not can_afford:
                bc, bw = (72, 68, 62), 1
            else:
                bc, bw = (158, 150, 138), 2
            pygame.draw.rect(self.screen, bc, rect, bw, border_radius=8)

            # Nummer badge
            badge = pygame.Rect(rect.x + 5, rect.y + 5, 18, 18)
            pygame.draw.rect(self.screen, (34, 30, 24), badge, border_radius=3)
            pygame.draw.rect(self.screen, (112, 102, 88), badge, 1, border_radius=3)
            ns = num_font.render(str(i + 1), True, WHITE)
            self.screen.blit(ns, (badge.centerx - ns.get_width() // 2,
                                  badge.centery - ns.get_height() // 2))

            # Icoon
            icon_sz = int(min(rect.width, rect.height) * 0.28)
            self._draw_tower_icon(tower_type, rect.centerx,
                                  rect.y + int(rect.height * 0.38),
                                  icon_sz, can_afford)

            # Naam
            nc = (205, 195, 178) if can_afford else (92, 88, 80)
            name_s = name_font.render(config["name"], True, nc)
            self.screen.blit(name_s, (rect.centerx - name_s.get_width() // 2,
                                      rect.bottom - 30))

            # Energy-badge
            cc = YELLOW if can_afford else (98, 90, 62)
            cost_s = cost_font.render(f"{config['cost']}E", True, cc)
            cb_x = rect.centerx - cost_s.get_width() // 2 - 4
            cb_y = rect.bottom - 16
            pygame.draw.rect(self.screen, (28, 25, 20),
                             (cb_x, cb_y, cost_s.get_width() + 8, 15), border_radius=3)
            self.screen.blit(cost_s, (cb_x + 4, cb_y + 1))

        # Tooltip bij hover (teken als laatste zodat het bovenop alles ligt)
        for tower_type, rect in self.tower_cards.items():
            if rect.collidepoint(mx, my):
                config = TOWER_TYPES[tower_type]
                desc = config.get("desc", "")
                if not desc:
                    break
                tip_font = pygame.font.SysFont(None, 20)
                tip_s = tip_font.render(desc, True, (230, 225, 210))
                tw = tip_s.get_width() + 16
                th = tip_s.get_height() + 10
                # Positie: boven de kaart, binnen scherm houden
                tx = max(4, min(rect.centerx - tw // 2, SCREEN_WIDTH - tw - 4))
                ty = rect.y - th - 6
                if ty < 0:
                    ty = rect.bottom + 6
                pygame.draw.rect(self.screen, (24, 22, 18), (tx, ty, tw, th), border_radius=6)
                pygame.draw.rect(self.screen, (160, 148, 110), (tx, ty, tw, th), 1, border_radius=6)
                self.screen.blit(tip_s, (tx + 8, ty + 5))
                break

    def handle_events(self) -> bool:
        """Verwerk input events.

        Returns:
            False als het spel moet stoppen.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = show_pause_menu(self.screen, self.clock)
                    if result == 'quit':
                        return False
                    if result == 'menu':
                        return 'menu'
                if event.key == pygame.K_SPACE and not self.wave_manager.wave_active:
                    self._wave_countdown = 0.0  # sla countdown over

                # P1: toren selectie met cijfertoetsen
                for i, tower_type in enumerate(self.tower_types_list):
                    if event.key == pygame.K_1 + i:
                        self.selected_tower_type = tower_type

                # P2: cursor en torenselectie (alleen lokale co-op)
                if self.multiplayer and self.net is None:
                    if event.key == pygame.K_UP:
                        self.p2_gy = max(0, self.p2_gy - 1)
                    elif event.key == pygame.K_DOWN:
                        self.p2_gy = min(GRID_ROWS - 1, self.p2_gy + 1)
                    elif event.key == pygame.K_LEFT:
                        self.p2_gx = max(0, self.p2_gx - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.p2_gx = min(GRID_COLS - 1, self.p2_gx + 1)
                    elif event.key == pygame.K_KP0:
                        self._p2_place_tower()
                    else:
                        kp_keys = [pygame.K_KP1, pygame.K_KP2,
                                   pygame.K_KP3, pygame.K_KP4]
                        for i, kp in enumerate(kp_keys):
                            if event.key == kp and i < len(self.tower_types_list):
                                self.p2_tower_type = self.tower_types_list[i]

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # rechtermuisknop → deselect
                    self.selected_tower = None
                elif event.button == 1:
                    if self.pause_btn.collidepoint(event.pos):
                        result = show_pause_menu(self.screen, self.clock)
                        if result == 'quit':
                            return False
                        if result == 'menu':
                            return 'menu'
                    else:
                        self._handle_click(event.pos)

        return True

    def _handle_click(self, pos: tuple[int, int]) -> None:
        """Verwerk een muisklik: torenselectie, verkoop of toren plaatsen."""
        mx, my = pos

        # Klik op perk-kaart
        if self.game_manager.has_pending_perk_choice():
            for perk_id, rect in self._perk_card_rects:
                if rect.collidepoint(mx, my):
                    self.game_manager.apply_perk(perk_id)
                    self._perk_card_rects = []
                    return
            return  # blokkeer andere clicks tijdens perk-keuze

        # Klik op upgrade-knop
        if self.selected_tower and self._upgrade_btns:
            for uid, btn in self._upgrade_btns.items():
                if btn.collidepoint(mx, my):
                    self.game_manager.upgrade_tower_at(
                        self.selected_tower.grid_x, self.selected_tower.grid_y,
                        uid, self.wave_manager.wave, self.wave_manager.wave_active)
                    return

        # Klik op verkoopknop
        if self._sell_btn and self._sell_btn.collidepoint(mx, my) and self.selected_tower:
            self.game_manager.sell_tower_at(
                self.selected_tower.grid_x, self.selected_tower.grid_y, self.grid_map)
            self.selected_tower = None
            self._sell_btn = None
            self._upgrade_btns = {}
            return

        # Klik op snelheidsknop
        if self.speed_btn.collidepoint(mx, my):
            self.game_manager.cycle_speed()
            return

        # Klik op een toren-selectiekaart
        for tower_type, rect in self.tower_cards.items():
            if rect.collidepoint(mx, my):
                self.selected_tower = None
                self.selected_tower_type = tower_type
                return

        # Klik buiten het grid → deselect
        grid_x = mx // TILE_SIZE
        grid_y = my // TILE_SIZE
        if not self.grid_map.is_within_bounds(grid_x, grid_y):
            self.selected_tower = None
            return

        # Klik op een cel met een toren → selecteer voor verkoop
        if self.grid_map.grid[grid_y][grid_x] == 2:
            tower = self.game_manager.get_tower_at(grid_x, grid_y)
            self.selected_tower = tower if tower != self.selected_tower else None
            return

        # Klik op lege cel → deselect en probeer toren te plaatsen
        self.selected_tower = None

        if not self.grid_map.can_place_tower(grid_x, grid_y):
            return

        if not self.game_manager.place_tower(self.selected_tower_type, grid_x, grid_y):
            return

        self.grid_map.place_tower(grid_x, grid_y)

        if self.net:
            self.net.send({
                "type": "PLACE_TOWER",
                "tower_type": self.selected_tower_type,
                "gx": grid_x,
                "gy": grid_y,
            })

    def _p2_place_tower(self) -> None:
        """Speler 2 plaatst een toren op de cursorpositie."""
        if not self.grid_map.can_place_tower(self.p2_gx, self.p2_gy):
            return
        if not self.game_manager.place_tower(self.p2_tower_type, self.p2_gx, self.p2_gy):
            return
        self.grid_map.place_tower(self.p2_gx, self.p2_gy)

    def _poll_network(self) -> None:
        """Verwerk inkomende berichten van de tegenstander."""
        while True:
            msg = self.net.poll()
            if msg is None:
                break
            t = msg.get("type")
            if t == "PLACE_TOWER":
                gx, gy = msg["gx"], msg["gy"]
                tt = msg["tower_type"]
                if self.grid_map.can_place_tower(gx, gy):
                    self.game_manager.place_tower(tt, gx, gy)
                    self.grid_map.place_tower(gx, gy)
            elif t == "START_WAVE" and not self.wave_manager.wave_active:
                self.game_manager.add_enemies(self.wave_manager.spawn_wave())
            elif t == "STATE_SYNC":
                # Host stuurt authoritative GPA/energy; gast accepteert deze
                if not self.is_host:
                    self.game_manager.gpa = msg.get("gpa", self.game_manager.gpa)
                    self.game_manager.energy = msg.get("energy", self.game_manager.energy)
            elif t == "PLAYER_LEFT":
                # Tegenstander is weggegaan
                font = pygame.font.SysFont(None, 48)
                surf = font.render("Tegenstander verliet het spel", True, (255, 80, 80))
                self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2,
                                        SCREEN_HEIGHT // 2 - surf.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(2500)
                self.net.disconnect()
                self.net = None

    def _draw_wave_countdown(self) -> None:
        """Toon een countdown-banner bovenin als er een wave op komst is."""
        secs = self._wave_countdown
        if secs <= 0:
            return
        next_wave = self.wave_manager.wave + 1
        grid_h = GRID_ROWS * TILE_SIZE

        # Banner hoogte en breedte
        bw, bh = 340, 54
        bx = SCREEN_WIDTH // 2 - bw // 2
        by = 10

        # Achtergrond
        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((10, 10, 18, 195))
        self.screen.blit(bg, (bx, by))
        pygame.draw.rect(self.screen, (80, 130, 210), (bx, by, bw, bh), 2, border_radius=8)

        # Tekst
        font_big = pygame.font.SysFont(None, 28, bold=True)
        font_sm  = pygame.font.SysFont(None, 20)

        label = font_big.render(f"Wave {next_wave} begint over {math.ceil(secs)}s", True, WHITE)
        self.screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, by + 7))

        hint = font_sm.render("SPACE om direct te starten", True, (130, 140, 170))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, by + 32))

        # Voortgangsbalk (totale wachttijd voor huidige fase)
        total = 5.0 if self.wave_manager.wave == 0 else 8.0
        frac = max(0.0, 1.0 - secs / total)
        bar_x, bar_y = bx + 10, by + bh + 4
        bar_w = bw - 20
        pygame.draw.rect(self.screen, (40, 44, 60), (bar_x, bar_y, bar_w, 5), border_radius=2)
        pygame.draw.rect(self.screen, (80, 130, 210),
                         (bar_x, bar_y, int(bar_w * frac), 5), border_radius=2)

    def _draw_tower_panel(self, tower) -> None:
        """Teken het info-panel boven de geselecteerde toren (upgrades + verkoop)."""
        from src.settings import TOWER_UPGRADES

        tower.draw_range(self.screen)
        mx, my = pygame.mouse.get_pos()

        # Verzamel beschikbare upgrades
        upgrades = self.game_manager.get_tower_upgrades(tower.tower_type)
        current_wave = self.wave_manager.wave
        wave_active = self.wave_manager.wave_active

        upgrade_rows: list[tuple[str, dict, bool, bool]] = []
        for uid, ucfg in upgrades.items():
            already = tower.has_upgrade(uid)
            can = self.game_manager.can_upgrade_tower(
                tower, uid, current_wave, wave_active)
            upgrade_rows.append((uid, ucfg, can, already))

        # Panel afmetingen
        pw = 200
        row_h = 28
        ph = 60 + len(upgrade_rows) * (row_h + 4) + (30 if upgrade_rows else 0)

        px = max(4, min(int(tower.x) - pw // 2, SCREEN_WIDTH - pw - 4))
        py = max(4, int(tower.y) - TILE_SIZE // 2 - ph - 6)

        panel = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(self.screen, (28, 26, 22), panel, border_radius=8)
        pygame.draw.rect(self.screen, (228, 202, 98), panel, 2, border_radius=8)

        nf = pygame.font.SysFont(None, 22, bold=True)
        sf = pygame.font.SysFont(None, 18)
        bf = pygame.font.SysFont(None, 19, bold=True)

        # Naam
        ns = nf.render(tower.name, True, WHITE)
        self.screen.blit(ns, (panel.centerx - ns.get_width() // 2, panel.y + 6))

        # Stats
        stats = sf.render(
            f"DMG {tower.damage:.1f}  RNG {tower.range}  SPD {tower.fire_rate:.1f}",
            True, (160, 155, 140))
        self.screen.blit(stats, (panel.centerx - stats.get_width() // 2, panel.y + 26))

        # Upgrade knoppen
        self._upgrade_btns = {}
        btn_y = panel.y + 46
        for uid, ucfg, can, already in upgrade_rows:
            btn = pygame.Rect(panel.x + 8, btn_y, pw - 16, row_h)
            self._upgrade_btns[uid] = btn

            if already:
                bg = (45, 55, 40)
                border = (80, 130, 70)
                label = f"{ucfg['name']} (actief)"
                lbl_col = (120, 180, 110)
            elif can:
                hov = btn.collidepoint(mx, my)
                bg = (55, 65, 35) if hov else (42, 50, 28)
                border = (140, 180, 80)
                cost = ucfg.get("cost", 0)
                label = f"{ucfg['name']} — {cost}E"
                lbl_col = (210, 230, 140)
            else:
                bg = (35, 32, 28)
                border = (65, 60, 52)
                cost = ucfg.get("cost", 0)
                # Check reden
                unlock_wave = ucfg.get("unlock_wave", 0)
                if current_wave < unlock_wave:
                    label = f"{ucfg['name']} (wave {unlock_wave}+)"
                elif already:
                    label = f"{ucfg['name']} (actief)"
                else:
                    label = f"{ucfg['name']} — {cost}E"
                lbl_col = (90, 85, 75)

            pygame.draw.rect(self.screen, bg, btn, border_radius=5)
            pygame.draw.rect(self.screen, border, btn, 1, border_radius=5)
            ls = bf.render(label, True, lbl_col)
            self.screen.blit(ls, (btn.centerx - ls.get_width() // 2,
                                  btn.centery - ls.get_height() // 2))
            btn_y += row_h + 4

        # Verkoopknop
        sell_y = btn_y + 4 if upgrade_rows else panel.y + 46
        refund = int(tower.energy_cost * 0.70)
        self._sell_btn = pygame.Rect(panel.x + 8, sell_y, pw - 16, row_h)
        hov = self._sell_btn.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (160, 55, 35) if hov else (110, 35, 20),
                         self._sell_btn, border_radius=5)
        pygame.draw.rect(self.screen, (220, 90, 60), self._sell_btn, 1, border_radius=5)
        sell_label = bf.render(f"Verkopen (+{refund}E)", True, WHITE)
        self.screen.blit(sell_label, (self._sell_btn.centerx - sell_label.get_width() // 2,
                                      self._sell_btn.centery - sell_label.get_height() // 2))

    def _draw_speed_btn(self) -> None:
        """Teken de snelheidsknop in de UI-balk."""
        speed = self.game_manager.speed_multiplier
        mx, my = pygame.mouse.get_pos()
        hov = self.speed_btn.collidepoint(mx, my)

        bg = (60, 58, 52) if hov else (40, 38, 34)
        pygame.draw.rect(self.screen, bg, self.speed_btn, border_radius=6)
        border_col = (228, 202, 98) if speed > 1.0 else (110, 104, 92)
        pygame.draw.rect(self.screen, border_col, self.speed_btn, 2, border_radius=6)

        # Label
        lf = pygame.font.SysFont(None, 18)
        ls = lf.render("SNELHEID", True, (120, 114, 100))
        self.screen.blit(ls, (self.speed_btn.centerx - ls.get_width() // 2,
                               self.speed_btn.y + 6))

        # Speed waarde
        speed_col = (255, 200, 50) if speed > 1.0 else WHITE
        sf = pygame.font.SysFont(None, 32, bold=True)
        label = f"{int(speed)}x" if speed == int(speed) else f"{speed}x"
        ss = sf.render(label, True, speed_col)
        self.screen.blit(ss, (self.speed_btn.centerx - ss.get_width() // 2,
                               self.speed_btn.centery - 2))

    def _draw_p2_cursor(self) -> None:
        """Teken de cursor van speler 2 op het grid."""
        x = self.p2_gx * TILE_SIZE
        y = self.p2_gy * TILE_SIZE
        can_place = self.grid_map.can_place_tower(self.p2_gx, self.p2_gy)
        color = (80, 200, 255) if can_place else (255, 80, 80)

        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        overlay.fill((*color, 55))
        self.screen.blit(overlay, (x, y))
        pygame.draw.rect(self.screen, color, (x, y, TILE_SIZE, TILE_SIZE), 2)

        lbl = self.small_font.render("P2", True, color)
        self.screen.blit(lbl, (x + 3, y + 3))

    def update(self, dt: float) -> None:
        """Update alle game objecten."""
        # Pauzeer als er een perk-keuze openstaat
        if self.game_manager.has_pending_perk_choice():
            return

        self.game_manager.update(dt, self.wave_manager)

        # Detecteer einde van een wave en reset countdown
        just_ended = self._was_wave_active and not self.wave_manager.wave_active
        self._was_wave_active = self.wave_manager.wave_active
        if just_ended:
            self._wave_countdown = 8.0

        # Automatische wave-start zodra countdown afloopt
        if not self.wave_manager.wave_active and not self.game_manager.game_over:
            self._wave_countdown -= dt
            if self._wave_countdown <= 0.0:
                self._wave_countdown = 0.0
                self.game_manager.add_enemies(self.wave_manager.spawn_wave())
                if self.net:
                    self.net.send({"type": "START_WAVE"})

    def draw(self) -> None:
        """Teken alles op het scherm."""
        self.screen.fill(GRASS_COLOR)

        # Teken grid
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile_idx = row * GRID_COLS + col
                if self.grid_map.grid[row][col] == 1:
                    # Pad
                    path_tile = get_path_tile(tile_idx)
                    if path_tile:
                        self.screen.blit(path_tile, rect)
                    else:
                        pygame.draw.rect(self.screen, PATH_COLOR, rect)
                else:
                    # Gras
                    grass_tile = get_grass_tile(tile_idx)
                    if grass_tile:
                        self.screen.blit(grass_tile, rect)
                pygame.draw.rect(self.screen, (80, 140, 60), rect, 1)

        # Teken torens
        for tower in self.game_manager.towers:
            tower.draw(self.screen)

        # Teken vijanden
        for enemy in self.game_manager.enemies:
            enemy.draw(self.screen)

        # Teken projectielen
        for proj in self.game_manager.projectiles:
            proj.draw(self.screen)

        # Range preview: toon bereik van geselecteerde toren op muispositie
        mx, my = pygame.mouse.get_pos()
        grid_area = my < GRID_ROWS * TILE_SIZE
        config = TOWER_TYPES.get(self.selected_tower_type)
        if config and grid_area:
            r = config["range"]
            if r > 0:
                # Snap naar grid-cel midden
                gx = mx // TILE_SIZE * TILE_SIZE + TILE_SIZE // 2
                gy = my // TILE_SIZE * TILE_SIZE + TILE_SIZE // 2
                range_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(range_surf, (255, 255, 255, 35), (r, r), r)
                pygame.draw.circle(range_surf, (255, 255, 255, 70), (r, r), r, 1)
                self.screen.blit(range_surf, (gx - r, gy - r))

        if self.multiplayer and self.net is None:
            self._draw_p2_cursor()

        # Wave-countdown banner
        if not self.wave_manager.wave_active and not self.game_manager.game_over:
            self._draw_wave_countdown()

        # Sell panel boven geselecteerde toren
        if self.selected_tower:
            self._draw_tower_panel(self.selected_tower)
        else:
            self._sell_btn = None
            self._upgrade_btns = {}

        # Teken UI
        self._draw_ui()
        self._draw_speed_btn()
        self._draw_pause_btn()

        # Perk-keuze overlay (bovenop alles)
        if self.game_manager.has_pending_perk_choice():
            self._draw_perk_overlay()

        pygame.display.flip()

    def _draw_pause_btn(self) -> None:
        """Teken de pauzeknop linksboven."""
        mx, my = pygame.mouse.get_pos()
        hovered = self.pause_btn.collidepoint(mx, my)
        bg = (80, 75, 70) if hovered else (50, 48, 44)
        pygame.draw.rect(self.screen, bg, self.pause_btn, border_radius=6)
        pygame.draw.rect(self.screen, (130, 120, 105), self.pause_btn, 2, border_radius=6)
        # Twee verticale balkjes (pauze-icoon)
        bx, by = self.pause_btn.x + 11, self.pause_btn.y + 10
        pygame.draw.rect(self.screen, WHITE, (bx, by, 6, 18))
        pygame.draw.rect(self.screen, WHITE, (bx + 10, by, 6, 18))

    def _draw_perk_overlay(self) -> None:
        """Teken de perk-keuze overlay (pauzeert het spel)."""
        choices = self.game_manager.get_pending_perk_choices()
        if not choices:
            return

        mx, my = pygame.mouse.get_pos()

        # Donkere overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Titel
        tf = pygame.font.SysFont(None, 42, bold=True)
        ts = tf.render("Kies een Perk", True, (255, 220, 80))
        self.screen.blit(ts, (SCREEN_WIDTH // 2 - ts.get_width() // 2, 80))

        sf = pygame.font.SysFont(None, 22)
        hint = sf.render(f"Wave {self.wave_manager.wave} voltooid!", True, (180, 175, 160))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 118))

        # Kaarten
        card_w, card_h = 220, 180
        gap = 24
        n = len(choices)
        total_w = n * card_w + (n - 1) * gap
        x0 = SCREEN_WIDTH // 2 - total_w // 2
        card_y = SCREEN_HEIGHT // 2 - card_h // 2

        nf = pygame.font.SysFont(None, 24, bold=True)
        df = pygame.font.SysFont(None, 19)
        stf = pygame.font.SysFont(None, 18)

        self._perk_card_rects = []
        for i, choice in enumerate(choices):
            cx = x0 + i * (card_w + gap)
            rect = pygame.Rect(cx, card_y, card_w, card_h)
            self._perk_card_rects.append((choice["id"], rect))

            hov = rect.collidepoint(mx, my)
            bg = (52, 48, 35) if hov else (35, 32, 26)
            border = (255, 220, 80) if hov else (140, 130, 100)

            pygame.draw.rect(self.screen, bg, rect, border_radius=10)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=10)

            # Naam
            ns = nf.render(choice["name"], True, (255, 230, 130))
            self.screen.blit(ns, (rect.centerx - ns.get_width() // 2, rect.y + 16))

            # Beschrijving — woordwrap
            desc = choice["description"]
            words = desc.split()
            lines: list[str] = []
            line = ""
            for w in words:
                test = f"{line} {w}".strip()
                if df.size(test)[0] <= card_w - 24:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = w
            if line:
                lines.append(line)

            for j, ln in enumerate(lines):
                ls = df.render(ln, True, (200, 195, 180))
                self.screen.blit(ls, (rect.centerx - ls.get_width() // 2,
                                      rect.y + 50 + j * 20))

            # Stacks indicator
            cur = choice["current_stacks"]
            mx_s = choice["max_stacks"]
            stack_txt = f"{'●' * cur}{'○' * (mx_s - cur)}  ({cur}/{mx_s})"
            ss = stf.render(stack_txt, True, (160, 155, 130))
            self.screen.blit(ss, (rect.centerx - ss.get_width() // 2, rect.bottom - 34))

            # "Kies" hint bij hover
            if hov:
                ks = stf.render("Klik om te kiezen", True, (255, 220, 80))
                self.screen.blit(ks, (rect.centerx - ks.get_width() // 2, rect.bottom - 16))

    def _draw_ui(self) -> None:
        """Teken de UI balk onderaan het scherm."""
        ui_y = GRID_ROWS * TILE_SIZE
        ui_rect = pygame.Rect(0, ui_y, SCREEN_WIDTH, SCREEN_HEIGHT - ui_y)
        pygame.draw.rect(self.screen, (40, 40, 50), ui_rect)
        pygame.draw.line(self.screen, WHITE, (0, ui_y), (SCREEN_WIDTH, ui_y), 2)

        # GPA
        gpa = self.game_manager.gpa
        gpa_color = GREEN if gpa > 7.0 else YELLOW if gpa > 5.5 else RED
        gpa_text = self.font.render(f"GPA: {gpa:.1f}", True, gpa_color)
        self.screen.blit(gpa_text, (20, ui_y + 10))

        # Energy
        energy_text = self.font.render(f"Energy: {self.game_manager.energy}", True, YELLOW)
        self.screen.blit(energy_text, (20, ui_y + 40))

        # Wave
        wave_text = self.font.render(f"Wave: {self.wave_manager.wave}", True, WHITE)
        self.screen.blit(wave_text, (180, ui_y + 10))

        if self.wave_manager.wave_active:
            active_hint = self.small_font.render("Wave bezig...", True, GRAY)
            self.screen.blit(active_hint, (180, ui_y + 40))

        # P2 indicator (alleen lokale co-op)
        if self.multiplayer and self.net is None:
            p2_color = (80, 200, 255)
            p2_name = TOWER_TYPES[self.p2_tower_type]["name"]
            p2_lbl = self.small_font.render("P2:", True, p2_color)
            p2_val = self.small_font.render(p2_name, True, WHITE)
            self.screen.blit(p2_lbl, (20, ui_y + 68))
            self.screen.blit(p2_val, (20 + p2_lbl.get_width() + 5, ui_y + 68))
            hint2 = self.small_font.render("Pijltjes + Numpad 0", True, GRAY)
            self.screen.blit(hint2, (20, ui_y + 88))
        elif self.net is not None:
            net_color = (80, 255, 160)
            role = "Host" if self.is_host else "Gast"
            net_lbl = self.small_font.render(f"Online ({role})", True, net_color)
            self.screen.blit(net_lbl, (20, ui_y + 68))

        # Toren selectiekaarten
        self._draw_tower_cards(ui_y)

    def run(self) -> str:
        """Start de game loop.

        Returns:
            'restart' → opnieuw spelen.
            'menu'    → terug naar hoofdmenu.
            'quit'    → afsluiten.
        """
        sync_timer = 0.0
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            sync_timer += dt

            result = self.handle_events()
            if result is False:
                return 'quit'
            if result == 'menu':
                return 'menu'

            # Verwerk inkomende netwerkberichten
            if self.net:
                self._poll_network()
                # Host stuurt elke seconde een STATE_SYNC
                if self.is_host and sync_timer >= 1.0:
                    sync_timer = 0.0
                    self.net.send({
                        "type": "STATE_SYNC",
                        "gpa": self.game_manager.gpa,
                        "energy": self.game_manager.energy,
                    })

            self.update(dt)
            self.draw()

            if self.game_manager.game_over:
                pygame.display.flip()
                return 'restart' if show_game_over_screen(
                    self.screen, self.clock,
                    self.wave_manager.wave,
                    self.game_manager.gpa,
                ) else 'quit'


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    while show_start_screen(screen, clock):
        if not show_tutorial_screen(screen, clock):
            break
        mode = show_mode_select_screen(screen, clock)
        if mode == 'back':
            continue

        if mode == 'online':
            lobby_result = show_network_lobby_screen(screen, clock)
            if lobby_result is None:
                continue  # gebruiker annuleerde lobby
            net_client, is_host = lobby_result
        else:
            net_client, is_host = None, False

        multiplayer = (mode == 'multi')

        while True:
            game = Game(
                screen=screen,
                clock=clock,
                multiplayer=multiplayer,
                network_client=net_client,
                is_host=is_host,
            )
            result = game.run()
            if net_client:
                net_client.disconnect()
            if result == 'quit':
                exit()
            if result == 'menu':
                break  # terug naar startscherm
            # 'restart' → nieuwe game in de inner loop (online: opnieuw verbinden is nodig)
            if mode == 'online':
                break  # bij online opnieuw verbinden via lobby
