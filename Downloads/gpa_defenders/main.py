"""GPA Defenders - Main entry point.

Start het spel door dit bestand te runnen:
    python main.py
"""

import math
import pygame
from src.ui.screens import (show_start_screen, show_pause_menu, show_tutorial_screen,
                            show_game_over_screen, show_mode_select_screen)
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
                 multiplayer: bool = False):
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
        self.wave_manager = WaveManager(self.grid_map.waypoints)
        self.game_manager = GameManager()

        self.selected_tower_type = "coffee"
        self.tower_types_list = list(TOWER_TYPES.keys())
        self.pause_btn = pygame.Rect(8, 8, 38, 38)
        self._setup_tower_cards()

        # Speler 2
        self.multiplayer = multiplayer
        if multiplayer:
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
            can_afford = self.game_manager.ects >= config["cost"]
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

            # ECTS-badge
            cc = YELLOW if can_afford else (98, 90, 62)
            cost_s = cost_font.render(f"{config['cost']} ECTS", True, cc)
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
                    self.game_manager.add_enemies(self.wave_manager.spawn_wave())

                # P1: toren selectie met cijfertoetsen
                for i, tower_type in enumerate(self.tower_types_list):
                    if event.key == pygame.K_1 + i:
                        self.selected_tower_type = tower_type

                # P2: cursor en torenselectie
                if self.multiplayer:
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
        """Verwerk een muisklik: torenselectie of toren plaatsen.

        Args:
            pos: (x, y) positie van de klik.
        """
        mx, my = pos

        # Klik op een toren-selectiekaart
        for tower_type, rect in self.tower_cards.items():
            if rect.collidepoint(mx, my):
                self.selected_tower_type = tower_type
                return

        grid_x = mx // TILE_SIZE
        grid_y = my // TILE_SIZE

        # Plaatsingsregels zitten in de map manager
        if not self.grid_map.can_place_tower(grid_x, grid_y):
            return

        # Check resources en plaats toren in game manager
        if not self.game_manager.place_tower(self.selected_tower_type, grid_x, grid_y):
            return

        # Markeer de cel als bezet op de map
        self.grid_map.place_tower(grid_x, grid_y)

    def _p2_place_tower(self) -> None:
        """Speler 2 plaatst een toren op de cursorpositie."""
        if not self.grid_map.can_place_tower(self.p2_gx, self.p2_gy):
            return
        if not self.game_manager.place_tower(self.p2_tower_type, self.p2_gx, self.p2_gy):
            return
        self.grid_map.place_tower(self.p2_gx, self.p2_gy)

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
        """Update alle game objecten.

        Args:
            dt: Delta time in seconden.
        """
        self.game_manager.update(dt, self.wave_manager)

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

        if self.multiplayer:
            self._draw_p2_cursor()

        # Teken UI
        self._draw_ui()
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

        # ECTS
        ects_text = self.font.render(f"ECTS: {self.game_manager.ects}", True, YELLOW)
        self.screen.blit(ects_text, (20, ui_y + 40))

        # Wave
        wave_text = self.font.render(f"Wave: {self.wave_manager.wave}", True, WHITE)
        self.screen.blit(wave_text, (180, ui_y + 10))

        if not self.wave_manager.wave_active:
            hint = self.small_font.render("[SPACE] Volgende wave", True, GRAY)
            self.screen.blit(hint, (180, ui_y + 40))

        # P2 indicator
        if self.multiplayer:
            p2_color = (80, 200, 255)
            p2_name = TOWER_TYPES[self.p2_tower_type]["name"]
            p2_lbl = self.small_font.render("P2:", True, p2_color)
            p2_val = self.small_font.render(p2_name, True, WHITE)
            self.screen.blit(p2_lbl, (20, ui_y + 68))
            self.screen.blit(p2_val, (20 + p2_lbl.get_width() + 5, ui_y + 68))
            hint2 = self.small_font.render("Pijltjes + Numpad 0", True, GRAY)
            self.screen.blit(hint2, (20, ui_y + 88))

        # Toren selectiekaarten
        self._draw_tower_cards(ui_y)

    def run(self) -> str:
        """Start de game loop.

        Returns:
            'restart' → opnieuw spelen.
            'menu'    → terug naar hoofdmenu.
            'quit'    → afsluiten.
        """
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            result = self.handle_events()
            if result is False:
                return 'quit'
            if result == 'menu':
                return 'menu'

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
        multiplayer = (mode == 'multi')
        while True:
            game = Game(screen=screen, clock=clock, multiplayer=multiplayer)
            result = game.run()
            if result == 'quit':
                exit()
            if result == 'menu':
                break  # terug naar startscherm
            # 'restart' → nieuwe game in de inner loop
