"""GPA Defenders - Main entry point.

Start het spel door dit bestand te runnen:
    python main.py
"""

import pygame
import sys
from src.ui.screens import show_start_screen, show_pause_menu
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    STARTING_GPA, FAILING_GPA, STARTING_ECTS,
    GRASS_COLOR, PATH_COLOR, BLACK, WHITE, RED, GREEN, YELLOW, GRAY,
    TOWER_TYPES,
)
from src.entities.tower import create_tower
from src.entities.enemy import Opdracht, Deadline, Tentamen, Professor
from src.entities.projectile import Projectile


class Game:
    """Hoofdclass die de game loop beheert.

    Attributes:
        screen: Het pygame scherm.
        clock: Pygame clock voor FPS.
        gpa: Huidige GPA score.
        ects: Huidige ECTS (geld).
        towers: Lijst van geplaatste torens.
        enemies: Lijst van actieve vijanden.
        projectiles: Lijst van actieve projectielen.
        wave: Huidige wave nummer.
        grid: 2D array met grid info (0=gras, 1=pad, 2=toren).
        waypoints: Lijst van waypoints voor het vijandpad.
        selected_tower: Huidig geselecteerd torentype.
    """

    def __init__(self, screen: pygame.Surface = None, clock: pygame.time.Clock = None):
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

        self.gpa = STARTING_GPA
        self.ects = STARTING_ECTS
        self.wave = 0
        self.game_over = False
        self.wave_active = False

        self.towers: list = []
        self.enemies: list = []
        self.projectiles: list = []

        self.selected_tower_type = "coffee"
        self.tower_types_list = list(TOWER_TYPES.keys())
        self.pause_btn = pygame.Rect(8, 8, 38, 38)

        self._setup_grid()

    def _setup_grid(self) -> None:
        """Maak het grid en definieer het vijandpad.

        TODO: Dit is een simpel voorbeeld-pad. Pas dit aan voor jullie spel!
        """
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        # Definieer waypoints (pad dat vijanden volgen)
        # Dit is een S-vormig pad als voorbeeld
        self.waypoints = [
            (0, 2 * TILE_SIZE + TILE_SIZE // 2),
            (4 * TILE_SIZE, 2 * TILE_SIZE + TILE_SIZE // 2),
            (4 * TILE_SIZE, 5 * TILE_SIZE + TILE_SIZE // 2),
            (10 * TILE_SIZE, 5 * TILE_SIZE + TILE_SIZE // 2),
            (10 * TILE_SIZE, 2 * TILE_SIZE + TILE_SIZE // 2),
            (SCREEN_WIDTH, 2 * TILE_SIZE + TILE_SIZE // 2),
        ]

        # Markeer pad-cellen in het grid
        for i in range(len(self.waypoints) - 1):
            x1, y1 = self.waypoints[i]
            x2, y2 = self.waypoints[i + 1]
            gx1, gy1 = int(x1 // TILE_SIZE), int(y1 // TILE_SIZE)
            gx2, gy2 = int(x2 // TILE_SIZE), int(y2 // TILE_SIZE)

            if gy1 == gy2:  # horizontaal
                for gx in range(min(gx1, gx2), max(gx1, gx2) + 1):
                    if 0 <= gx < GRID_COLS and 0 <= gy1 < GRID_ROWS:
                        self.grid[gy1][gx] = 1
            elif gx1 == gx2:  # verticaal
                for gy in range(min(gy1, gy2), max(gy1, gy2) + 1):
                    if 0 <= gx1 < GRID_COLS and 0 <= gy < GRID_ROWS:
                        self.grid[gy][gx1] = 1

    def spawn_wave(self) -> None:
        """Start een nieuwe wave met vijanden.

        TODO: Maak dit uitgebreider met meer variatie per wave!
        """
        self.wave += 1
        self.wave_active = True

        # Simpele wave logica: meer en sterkere vijanden per wave
        for i in range(3 + self.wave * 2):
            # Verschuif de startpositie zodat ze niet allemaal tegelijk spawnen
            delayed_waypoints = [
                (self.waypoints[0][0] - i * 40, self.waypoints[0][1])
            ] + self.waypoints[:]

            if self.wave < 3:
                self.enemies.append(Opdracht(delayed_waypoints))
            elif self.wave < 5:
                if i % 3 == 0:
                    self.enemies.append(Deadline(delayed_waypoints))
                else:
                    self.enemies.append(Opdracht(delayed_waypoints))
            elif self.wave < 8:
                if i % 5 == 0:
                    self.enemies.append(Tentamen(delayed_waypoints))
                elif i % 3 == 0:
                    self.enemies.append(Deadline(delayed_waypoints))
                else:
                    self.enemies.append(Opdracht(delayed_waypoints))
            else:
                if i == 0:
                    self.enemies.append(Professor(delayed_waypoints))
                elif i % 4 == 0:
                    self.enemies.append(Tentamen(delayed_waypoints))
                else:
                    self.enemies.append(Deadline(delayed_waypoints))

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
                    if not show_pause_menu(self.screen, self.clock):
                        return False
                    return True
                if event.key == pygame.K_SPACE and not self.wave_active:
                    self.spawn_wave()

                # Toren selectie met cijfertoetsen
                for i, tower_type in enumerate(self.tower_types_list):
                    if event.key == pygame.K_1 + i:
                        self.selected_tower_type = tower_type

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pause_btn.collidepoint(event.pos):
                    if not show_pause_menu(self.screen, self.clock):
                        return False
                else:
                    self._handle_click(event.pos)

        return True

    def _handle_click(self, pos: tuple[int, int]) -> None:
        """Verwerk een muisklik om een toren te plaatsen.

        Args:
            pos: (x, y) positie van de klik.
        """
        mx, my = pos
        grid_x = mx // TILE_SIZE
        grid_y = my // TILE_SIZE

        # Check of het binnen het grid valt
        if grid_x < 0 or grid_x >= GRID_COLS or grid_y < 0 or grid_y >= GRID_ROWS:
            return

        # Check of de cel vrij is (niet pad, niet bezet)
        if self.grid[grid_y][grid_x] != 0:
            return

        # Check of we genoeg ECTS hebben
        cost = TOWER_TYPES[self.selected_tower_type]["cost"]
        if self.ects < cost:
            return

        # Plaats de toren
        tower = create_tower(self.selected_tower_type, grid_x, grid_y)
        self.towers.append(tower)
        self.grid[grid_y][grid_x] = 2
        self.ects -= cost

    def update(self, dt: float) -> None:
        """Update alle game objecten.

        Args:
            dt: Delta time in seconden.
        """
        if self.game_over:
            return

        # Update torens en maak projectielen
        for tower in self.towers:
            result = tower.update(dt, self.enemies)
            if result:
                proj = Projectile(
                    result["x"], result["y"], result["target"],
                    result["damage"], result["speed"], result["color"],
                    result.get("slow_factor", 0), result.get("slow_duration", 0),
                )
                self.projectiles.append(proj)

        # Update vijanden
        for enemy in self.enemies:
            enemy.update(dt)
            if enemy.reached_end:
                self.gpa -= enemy.gpa_damage
                enemy.alive = False
            if not enemy.alive and not enemy.reached_end:
                self.ects += enemy.ects_reward

        # Update projectielen
        for proj in self.projectiles:
            proj.update(dt)

        # Verwijder dode objecten
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Check wave klaar
        if self.wave_active and len(self.enemies) == 0:
            self.wave_active = False

        # Check game over
        if self.gpa <= FAILING_GPA:
            self.game_over = True

    def draw(self) -> None:
        """Teken alles op het scherm."""
        self.screen.fill(GRASS_COLOR)

        # Teken grid
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.grid[row][col] == 1:
                    pygame.draw.rect(self.screen, PATH_COLOR, rect)
                pygame.draw.rect(self.screen, (80, 140, 60), rect, 1)

        # Teken torens
        for tower in self.towers:
            tower.draw(self.screen)

        # Teken vijanden
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Teken projectielen
        for proj in self.projectiles:
            proj.draw(self.screen)

        # Teken UI
        self._draw_ui()
        self._draw_pause_btn()

        if self.game_over:
            self._draw_game_over()

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
        pygame.draw.rect(self.screen, WHITE, (bx,      by, 6, 18))
        pygame.draw.rect(self.screen, WHITE, (bx + 10, by, 6, 18))

    def _draw_ui(self) -> None:
        """Teken de UI balk onderaan het scherm."""
        ui_y = GRID_ROWS * TILE_SIZE
        ui_rect = pygame.Rect(0, ui_y, SCREEN_WIDTH, SCREEN_HEIGHT - ui_y)
        pygame.draw.rect(self.screen, (40, 40, 50), ui_rect)
        pygame.draw.line(self.screen, WHITE, (0, ui_y), (SCREEN_WIDTH, ui_y), 2)

        # GPA
        gpa_color = GREEN if self.gpa > 7.0 else YELLOW if self.gpa > 5.5 else RED
        gpa_text = self.font.render(f"GPA: {self.gpa:.1f}", True, gpa_color)
        self.screen.blit(gpa_text, (20, ui_y + 10))

        # ECTS
        ects_text = self.font.render(f"ECTS: {self.ects}", True, YELLOW)
        self.screen.blit(ects_text, (20, ui_y + 40))

        # Wave
        wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)
        self.screen.blit(wave_text, (180, ui_y + 10))

        if not self.wave_active:
            hint = self.small_font.render("[SPACE] Volgende wave", True, GRAY)
            self.screen.blit(hint, (180, ui_y + 40))

        # Toren selectie
        x_offset = 380
        for i, tower_type in enumerate(self.tower_types_list):
            config = TOWER_TYPES[tower_type]
            is_selected = tower_type == self.selected_tower_type
            color = WHITE if is_selected else GRAY
            border = 2 if is_selected else 0

            box = pygame.Rect(x_offset, ui_y + 8, 140, 55)
            if is_selected:
                pygame.draw.rect(self.screen, (60, 60, 80), box)
            pygame.draw.rect(self.screen, color, box, max(border, 1))

            name = self.small_font.render(f"[{i+1}] {config['name']}", True, color)
            cost = self.small_font.render(f"{config['cost']} ECTS", True, YELLOW)
            self.screen.blit(name, (x_offset + 5, ui_y + 12))
            self.screen.blit(cost, (x_offset + 5, ui_y + 34))

            x_offset += 150

    def _draw_game_over(self) -> None:
        """Teken het game over scherm."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont(None, 72)
        text = big_font.render("GEZAKT!", True, RED)
        self.screen.blit(
            text,
            (SCREEN_WIDTH // 2 - text.get_width() // 2,
             SCREEN_HEIGHT // 2 - text.get_height() // 2)
        )

        sub_text = self.font.render(
            f"Je hebt {self.wave} waves overleefd!", True, WHITE
        )
        self.screen.blit(
            sub_text,
            (SCREEN_WIDTH // 2 - sub_text.get_width() // 2,
             SCREEN_HEIGHT // 2 + 50)
        )

    def run(self) -> None:
        """Start de game loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    if show_start_screen(screen, clock):
        game = Game(screen=screen, clock=clock)
        game.run()
