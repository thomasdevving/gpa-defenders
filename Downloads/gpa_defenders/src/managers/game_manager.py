"""Core game-state updates voor GPA Defenders."""

from typing import TYPE_CHECKING

from src.entities.projectile import Projectile
from src.entities.tower import create_tower
from src.settings import STARTING_GPA, STARTING_ECTS, FAILING_GPA, TOWER_TYPES

if TYPE_CHECKING:
    from src.managers.wave_manager import WaveManager


class GameManager:
    """Beheert combat, resources en verliesconditie."""

    def __init__(self):
        self.gpa = STARTING_GPA
        self.ects = STARTING_ECTS
        self.game_over = False

        self.towers: list = []
        self.enemies: list = []
        self.projectiles: list = []

    def can_afford_tower(self, tower_type: str) -> bool:
        """Check of de speler genoeg ECTS heeft voor een toren."""
        cost = TOWER_TYPES[tower_type]["cost"]
        return self.ects >= cost

    def place_tower(self, tower_type: str, grid_x: int, grid_y: int) -> bool:
        """Plaats een toren als de speler genoeg ECTS heeft."""
        if not self.can_afford_tower(tower_type):
            return False

        cost = TOWER_TYPES[tower_type]["cost"]
        tower = create_tower(tower_type, grid_x, grid_y)
        self.towers.append(tower)
        self.ects -= cost
        return True

    def add_enemies(self, enemies: list) -> None:
        """Voeg een batch vijanden toe aan het speelveld."""
        self.enemies.extend(enemies)

    def update(self, dt: float, wave_manager: "WaveManager") -> None:
        """Update combat, rewards, wave status en fail condition."""
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
        wave_manager.update_wave_state(self.enemies)

        # Check game over
        if self.gpa <= FAILING_GPA:
            self.game_over = True
