"""Toren classes voor GPA Defenders.

Alle torens erven van Tower en hebben uniek aanvalsgedrag via polymorphism.
"""

import pygame
import math
from src.entities.entity import Entity
from src.entities.enemy import Enemy
from src.settings import TOWER_TYPES, BLACK, TILE_SIZE


class Tower(Entity):
    """Base class voor alle torens.

    Torens staan op een vaste plek en schieten op vijanden binnen bereik.

    Attributes:
        tower_type: Type toren (coffee, study_group, etc.).
        damage: Schade per schot.
        range: Bereik in pixels.
        fire_rate: Schoten per seconde.
        fire_cooldown: Tijd tot volgend schot.
        color: Kleur van de toren.
        target: Huidige vijand waarop geschoten wordt.
    """

    def __init__(self, tower_type: str, grid_x: int, grid_y: int):
        # Centreer de toren in de grid cel
        pixel_x = grid_x * TILE_SIZE + TILE_SIZE // 2
        pixel_y = grid_y * TILE_SIZE + TILE_SIZE // 2
        super().__init__(pixel_x, pixel_y)

        config = TOWER_TYPES[tower_type]
        self.tower_type = tower_type
        self.name = config["name"]
        self.costs = config.get("costs", {"energy": config["cost"]})
        self.energy_cost = self.costs.get("energy", 0)
        # Backward compatibility for current UI/logic paths.
        self.cost = self.energy_cost
        self.damage = config["damage"]
        self.range = config["range"]
        self.fire_rate = config["fire_rate"]
        self.color = config["color"]
        self.projectile_color = config["projectile_color"]
        self.projectile_speed = config["projectile_speed"]

        self.grid_x = grid_x
        self.grid_y = grid_y
        self.fire_cooldown = 0.0
        self.target = None
        self.size = TILE_SIZE // 2 - 4

    def find_target(self, enemies: list[Enemy]) -> Enemy | None:
        """Zoek de dichtstbijzijnde vijand binnen bereik.

        Args:
            enemies: Lijst van actieve vijanden.

        Returns:
            De dichtstbijzijnde vijand, of None.
        """
        closest = None
        closest_dist = float("inf")

        for enemy in enemies:
            if not enemy.alive or enemy.reached_end:
                continue
            dist = self.distance_to(enemy)
            if dist <= self.range and dist < closest_dist:
                closest = enemy
                closest_dist = dist

        return closest

    def can_fire(self) -> bool:
        """Check of de toren kan schieten."""
        return self.fire_cooldown <= 0 and self.target is not None

    def fire(self) -> dict | None:
        """Schiet op het huidige target.

        Returns:
            Projectile info dict als er geschoten wordt, anders None.
        """
        if not self.can_fire():
            return None

        self.fire_cooldown = 1.0 / self.fire_rate

        return {
            "x": self.x,
            "y": self.y,
            "target": self.target,
            "damage": self.damage,
            "color": self.projectile_color,
            "speed": self.projectile_speed,
            "tower_type": self.tower_type,
        }

    def update(self, dt: float, enemies: list[Enemy] | None = None) -> dict | None:
        """Update de toren: zoek target en schiet.

        Args:
            dt: Delta time in seconden.
            enemies: Lijst van vijanden om op te schieten.

        Returns:
            Projectile info als er geschoten wordt.
        """
        self.fire_cooldown -= dt

        if enemies:
            self.target = self.find_target(enemies)

        return self.fire()

    def draw(self, screen: pygame.Surface) -> None:
        """Teken de toren.

        Args:
            screen: Het pygame scherm.
        """
        # Vierkant als basis
        rect = pygame.Rect(
            int(self.x) - self.size,
            int(self.y) - self.size,
            self.size * 2,
            self.size * 2,
        )
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        # Bereik tonen als geselecteerd (kan later toegevoegd worden)

    def draw_range(self, screen: pygame.Surface) -> None:
        """Teken het bereik van de toren (voor selectie).

        Args:
            screen: Het pygame scherm.
        """
        range_surface = pygame.Surface(
            (self.range * 2, self.range * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            range_surface, (255, 255, 255, 40),
            (self.range, self.range), self.range
        )
        screen.blit(range_surface, (int(self.x) - self.range, int(self.y) - self.range))


class CoffeeTower(Tower):
    """Basistoren. Schiet cafeïne-projectielen. Betrouwbaar en goedkoop."""

    def __init__(self, grid_x: int, grid_y: int):
        super().__init__("coffee", grid_x, grid_y)

    def draw(self, screen: pygame.Surface) -> None:
        """Teken een koffiebeker."""
        super().draw(screen)
        # Koffie-icoon: kleine stoom lijntjes
        for i in range(3):
            start_x = int(self.x) - 6 + i * 6
            pygame.draw.line(
                screen, (200, 200, 200),
                (start_x, int(self.y) - self.size - 2),
                (start_x, int(self.y) - self.size - 8), 1
            )


class StudyGroupTower(Tower):
    """Vertraagt vijanden in plaats van veel schade te doen."""

    def __init__(self, grid_x: int, grid_y: int):
        super().__init__("study_group", grid_x, grid_y)
        config = TOWER_TYPES["study_group"]
        self.slow_factor = config["slow_factor"]
        self.slow_duration = config["slow_duration"]

    def fire(self) -> dict | None:
        """Schiet een vertraagd projectiel."""
        result = super().fire()
        if result:
            result["slow_factor"] = self.slow_factor
            result["slow_duration"] = self.slow_duration
        return result

    def draw(self, screen: pygame.Surface) -> None:
        """Teken een studiegroep icoon (meerdere kleine cirkels)."""
        super().draw(screen)
        # Teken kleine "personen" op de toren
        offsets = [(-5, -3), (5, -3), (0, 4)]
        for ox, oy in offsets:
            pygame.draw.circle(
                screen, (200, 220, 255),
                (int(self.x) + ox, int(self.y) + oy), 3
            )


class TutorTower(Tower):
    """Hoge schade, langzaam. Goed tegen sterke vijanden."""

    def __init__(self, grid_x: int, grid_y: int):
        super().__init__("tutor", grid_x, grid_y)

    def draw(self, screen: pygame.Surface) -> None:
        """Teken een tutor icoon (groot met bril)."""
        super().draw(screen)
        # Bril-icoon
        pygame.draw.circle(screen, (200, 200, 200), (int(self.x) - 4, int(self.y) - 2), 4, 1)
        pygame.draw.circle(screen, (200, 200, 200), (int(self.x) + 4, int(self.y) - 2), 4, 1)
        pygame.draw.line(screen, (200, 200, 200), (int(self.x), int(self.y) - 2), (int(self.x), int(self.y) - 2), 1)


class EnergyDrinkTower(Tower):
    """Zeer snelle vuursnelheid, maar lage schade per schot."""

    def __init__(self, grid_x: int, grid_y: int):
        super().__init__("energy_drink", grid_x, grid_y)

    def draw(self, screen: pygame.Surface) -> None:
        """Teken een energy drink met bliksem."""
        super().draw(screen)
        # Bliksem icoon
        points = [
            (int(self.x) - 2, int(self.y) - 6),
            (int(self.x) + 2, int(self.y) - 1),
            (int(self.x) - 1, int(self.y) - 1),
            (int(self.x) + 3, int(self.y) + 6),
        ]
        pygame.draw.lines(screen, BLACK, False, points, 2)


# Factory functie om torens aan te maken
def create_tower(tower_type: str, grid_x: int, grid_y: int) -> Tower:
    """Maak een toren aan op basis van type.

    Args:
        tower_type: Het type toren.
        grid_x: Grid x-positie.
        grid_y: Grid y-positie.

    Returns:
        Een Tower subclass instantie.

    Raises:
        ValueError: Als het tower type onbekend is.
    """
    tower_classes = {
        "coffee": CoffeeTower,
        "study_group": StudyGroupTower,
        "tutor": TutorTower,
        "energy_drink": EnergyDrinkTower,
    }

    if tower_type not in tower_classes:
        raise ValueError(f"Onbekend toren type: {tower_type}")

    return tower_classes[tower_type](grid_x, grid_y)
