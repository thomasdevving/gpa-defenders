"""Projectiel classes voor GPA Defenders."""

import pygame
import math
from src.entities.entity import Entity
from src.entities.enemy import Enemy
from src.settings import BLACK


class Projectile(Entity):
    """Een projectiel dat van een toren naar een vijand vliegt.

    Attributes:
        target: De vijand waar het projectiel naartoe vliegt.
        damage: Schade bij impact.
        speed: Snelheid in pixels per seconde.
        color: Kleur van het projectiel.
        slow_factor: Vertragingsfactor (optioneel).
        slow_duration: Duur van vertraging (optioneel).
    """

    def __init__(self, x: float, y: float, target: Enemy,
                 damage: float, speed: float, color: tuple,
                 slow_factor: float = 0.0, slow_duration: float = 0.0,
                 slow_source_id: int | None = None):
        super().__init__(x, y)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color
        self.slow_factor = slow_factor
        self.slow_duration = slow_duration
        self.slow_source_id = slow_source_id
        self.radius = 4

    def update(self, dt: float) -> None:
        """Beweeg richting het target.

        Args:
            dt: Delta time in seconden.
        """
        if not self.alive:
            return

        # Als target dood is, verdwijn
        if not self.target.alive:
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # Check hit
        if distance < self.target.radius:
            self.target.take_damage(self.damage)
            if self.slow_factor > 0:
                self.target.apply_slow(
                    self.slow_factor,
                    self.slow_duration,
                    self.slow_source_id,
                )
            self.alive = False
            return

        # Beweeg
        move = self.speed * dt
        self.x += (dx / distance) * move
        self.y += (dy / distance) * move

    def draw(self, screen: pygame.Surface) -> None:
        """Teken het projectiel.

        Args:
            screen: Het pygame scherm.
        """
        if not self.alive:
            return

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 1)
