"""GPA Defenders - Main entry point.

Start het spel door dit bestand te runnen:
    python main.py
"""

import pygame
import sys
from src.ui.screens import show_start_screen
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

        self.grid_map = GridMap()
        self.wave_manager = WaveManager(self.grid_map.waypoints)
        self.game_manager = GameManager()

        self.selected_tower_type = "coffee"
        self.tower_types_list = list(TOWER_TYPES.keys())

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
                    return False
                if event.key == pygame.K_SPACE and not self.wave_manager.wave_active:
                    self.game_manager.add_enemies(self.wave_manager.spawn_wave())

                # Toren selectie met cijfertoetsen
                for i, tower_type in enumerate(self.tower_types_list):
                    if event.key == pygame.K_1 + i:
                        self.selected_tower_type = tower_type

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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

        # Plaatsingsregels zitten in de map manager
        if not self.grid_map.can_place_tower(grid_x, grid_y):
            return

        # Check resources en plaats toren in game manager
        if not self.game_manager.place_tower(self.selected_tower_type, grid_x, grid_y):
            return

        # Markeer de cel als bezet op de map
        self.grid_map.place_tower(grid_x, grid_y)

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

        # Teken UI
        self._draw_ui()

        if self.game_manager.game_over:
            self._draw_game_over()

        pygame.display.flip()

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
            f"Je hebt {self.wave_manager.wave} waves overleefd!", True, WHITE
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
