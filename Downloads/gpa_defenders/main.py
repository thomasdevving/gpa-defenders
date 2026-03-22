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

        self.selected_tower_type = "coffee"
        self.tower_types_list = list(TOWER_TYPES.keys())
        self.pause_btn = pygame.Rect(8, 8, 38, 38)
        self._setup_tower_cards()

        # Netwerk (online multiplayer)
        self.net: NetworkClient | None = network_client
        self.is_host = is_host

        # Geselecteerde toren (voor verkoop-UI)
        self.selected_tower = None
        self._sell_btn: pygame.Rect | None = None

        # Snelheidsknop
        ui_y = GRID_ROWS * TILE_SIZE
        self.speed_btn = pygame.Rect(348, ui_y + 8, 82, 58)

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
        """Bereken de klikbare kaart-rects voor torenselectie."""
        ui_y = GRID_ROWS * TILE_SIZE
        card_w, card_h, gap = 110, 165, 14
        n = len(self.tower_types_list)
        total_w = n * card_w + (n - 1) * gap
        # Centreer de kaarten in het rechtergedeelte van de UI-balk
        x0 = (SCREEN_WIDTH + 360) // 2 - total_w // 2
        card_top = ui_y + 13
        self.tower_cards: dict[str, pygame.Rect] = {}
        for i, t in enumerate(self.tower_types_list):
            self.tower_cards[t] = pygame.Rect(x0 + i * (card_w + gap), card_top, card_w, card_h)

    def _draw_tower_icon(self, tower_type: str, cx: int, cy: int,
                         sz: int, active: bool) -> None:
        """Teken het icoon voor een torentype."""
        col = TOWER_TYPES[tower_type]["color"] if active else (68, 65, 60)

        if tower_type == "coffee":
            # Koffiekopje
            hw = int(sz * 0.52)
            pts = [(cx - hw, cy - int(sz * 0.08)),
                   (cx + hw, cy - int(sz * 0.08)),
                   (cx + int(hw * 0.72), cy + int(sz * 0.5)),
                   (cx - int(hw * 0.72), cy + int(sz * 0.5))]
            pygame.draw.polygon(self.screen, col, pts)
            pygame.draw.polygon(self.screen, (40, 25, 10), pts, 2)
            # Oor
            pygame.draw.arc(self.screen, col,
                            pygame.Rect(cx + int(hw * 0.58), cy, int(hw * 0.7), int(sz * 0.32)),
                            -math.pi * 0.5, math.pi * 0.5, 3)
            # Stoom
            sc = (185, 188, 205) if active else (70, 68, 65)
            for ox in (-int(sz * 0.2), 0, int(sz * 0.2)):
                for k in range(2):
                    y1 = cy - int(sz * 0.18) - k * 7
                    pygame.draw.line(self.screen, sc,
                                     (cx + ox, y1),
                                     (cx + ox + ((-1) ** k) * 4, y1 - 5), 2)

        elif tower_type == "study_group":
            # Twee studentenfiguren
            skin = (200, 168, 128) if active else (68, 65, 60)
            for ox in (-int(sz * 0.28), int(sz * 0.28)):
                pygame.draw.circle(self.screen, skin,
                                   (cx + ox, cy - int(sz * 0.24)), int(sz * 0.17))
                pygame.draw.line(self.screen, col,
                                 (cx + ox, cy - int(sz * 0.06)),
                                 (cx + ox, cy + int(sz * 0.32)), 3)
                pygame.draw.line(self.screen, col,
                                 (cx + ox - int(sz * 0.18), cy + int(sz * 0.1)),
                                 (cx + ox + int(sz * 0.18), cy + int(sz * 0.1)), 2)

        elif tower_type == "tutor":
            # Opengeslagen boek
            hw, hh = int(sz * 0.46), int(sz * 0.36)
            page1 = (228, 222, 208) if active else (72, 70, 65)
            page2 = (244, 240, 226) if active else (78, 75, 70)
            lc = (148, 138, 122) if active else (58, 56, 52)
            pygame.draw.rect(self.screen, page1, (cx - hw, cy - hh, hw, hh * 2))
            pygame.draw.rect(self.screen, page2, (cx,      cy - hh, hw, hh * 2))
            pygame.draw.line(self.screen, col, (cx, cy - hh), (cx, cy + hh), 2)
            for k in range(4):
                y = cy - hh + 7 + k * max(1, (hh * 2 - 14) // 4)
                pygame.draw.line(self.screen, lc, (cx - hw + 5, y), (cx - 4, y), 1)
                pygame.draw.line(self.screen, lc, (cx + 4,      y), (cx + hw - 5, y), 1)

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
            pygame.draw.polygon(self.screen, col, pts)
            if active:
                pygame.draw.polygon(self.screen, (255, 160, 30), pts, 2)

    def _draw_tower_cards(self, ui_y: int) -> None:
        """Teken de klikbare torenselectiekaarten."""
        mx, my = pygame.mouse.get_pos()
        rects = list(self.tower_cards.values())

        # Houten tray achter de kaarten
        pad = 8
        tray = pygame.Rect(
            rects[0].x - pad - 6,
            rects[0].y - pad,
            rects[-1].right - rects[0].x + (pad + 6) * 2,
            rects[0].height + pad * 2,
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
            self._draw_tower_icon(tower_type, rect.centerx,
                                  rect.y + int(rect.height * 0.42),
                                  int(min(rect.width, rect.height) * 0.33), can_afford)

            # Naam
            nc = (205, 195, 178) if can_afford else (92, 88, 80)
            name_s = name_font.render(config["name"], True, nc)
            self.screen.blit(name_s, (rect.centerx - name_s.get_width() // 2,
                                      rect.bottom - 38))

            # Energy-badge
            cc = YELLOW if can_afford else (98, 90, 62)
            cost_s = cost_font.render(f"{config['cost']} Energy", True, cc)
            cb_x = rect.centerx - cost_s.get_width() // 2 - 5
            cb_y = rect.bottom - 20
            pygame.draw.rect(self.screen, (28, 25, 20),
                             (cb_x, cb_y, cost_s.get_width() + 10, 17), border_radius=3)
            self.screen.blit(cost_s, (cb_x + 5, cb_y + 1))

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

        # Klik op verkoopknop (onderdeel van de sell panel)
        if self._sell_btn and self._sell_btn.collidepoint(mx, my) and self.selected_tower:
            self.game_manager.sell_tower_at(
                self.selected_tower.grid_x, self.selected_tower.grid_y, self.grid_map)
            self.selected_tower = None
            self._sell_btn = None
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

    def _draw_sell_panel(self, tower) -> None:
        """Teken de verkooppanel boven de geselecteerde toren."""
        # Bereikscirkel
        tower.draw_range(self.screen)

        pw, ph = 178, 84
        # Positie boven de toren, binnen scherm houden
        px = max(4, min(int(tower.x) - pw // 2, SCREEN_WIDTH - pw - 4))
        py = max(4, int(tower.y) - TILE_SIZE // 2 - ph - 6)

        # Achtergrond
        panel = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(self.screen, (28, 26, 22), panel, border_radius=8)
        pygame.draw.rect(self.screen, (228, 202, 98), panel, 2, border_radius=8)

        # Naam
        nf = pygame.font.SysFont(None, 22, bold=True)
        ns = nf.render(tower.name, True, WHITE)
        self.screen.blit(ns, (panel.centerx - ns.get_width() // 2, panel.y + 8))

        # Verkoopwaarde
        refund = int(tower.energy_cost * 0.70)
        vf = pygame.font.SysFont(None, 20)
        vs = vf.render(f"Verkoopt voor {refund} Energy", True, (170, 165, 140))
        self.screen.blit(vs, (panel.centerx - vs.get_width() // 2, panel.y + 28))

        # Verkoopknop
        bw, bh = pw - 20, 26
        self._sell_btn = pygame.Rect(panel.x + 10, panel.bottom - bh - 8, bw, bh)
        mx, my = pygame.mouse.get_pos()
        hov = self._sell_btn.collidepoint(mx, my)
        pygame.draw.rect(self.screen, (160, 55, 35) if hov else (110, 35, 20),
                         self._sell_btn, border_radius=5)
        pygame.draw.rect(self.screen, (220, 90, 60), self._sell_btn, 1, border_radius=5)
        bf = pygame.font.SysFont(None, 20, bold=True)
        bs = bf.render("Verkopen", True, WHITE)
        self.screen.blit(bs, (self._sell_btn.centerx - bs.get_width() // 2,
                               self._sell_btn.centery - bs.get_height() // 2))

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
                if self.grid_map.grid[row][col] == 1:
                    pygame.draw.rect(self.screen, PATH_COLOR, rect)
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

        if self.multiplayer and self.net is None:
            self._draw_p2_cursor()

        # Wave-countdown banner
        if not self.wave_manager.wave_active and not self.game_manager.game_over:
            self._draw_wave_countdown()

        # Sell panel boven geselecteerde toren
        if self.selected_tower:
            self._draw_sell_panel(self.selected_tower)
        else:
            self._sell_btn = None

        # Teken UI
        self._draw_ui()
        self._draw_speed_btn()
        self._draw_pause_btn()

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
