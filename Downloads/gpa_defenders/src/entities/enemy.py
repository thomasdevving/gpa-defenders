"""Vijand classes voor GPA Defenders.

Alle vijanden erven van Enemy en hebben uniek gedrag via polymorphism.
"""

import pygame
import math
from src.entities.entity import Entity
from src.settings import ENEMY_TYPES, RED, GREEN, WHITE, BLACK


class Enemy(Entity):
    """Base class voor alle vijanden.

    Vijanden volgen een pad van waypoints en beschadigen je GPA
    als ze het einde bereiken.

    Attributes:
        enemy_type: Type vijand (opdracht, deadline, etc.).
        hp: Huidige hitpoints.
        max_hp: Maximale hitpoints.
        speed: Basissnelheid in pixels per seconde.
        current_speed: Huidige snelheid (kan vertraagd zijn).
        gpa_damage: Hoeveel GPA-schade bij het bereiken van het einde.
        ects_reward: Hoeveel ECTS je krijgt bij het verslaan.
        color: Kleur van de vijand.
        waypoints: Lijst van (x, y) punten om te volgen.
        waypoint_index: Huidige waypoint index.
        slow_timer: Resterende tijd van slow effect.
    """

    def __init__(self, enemy_type: str, waypoints: list[tuple[int, int]]):
        start_x, start_y = waypoints[0]
        super().__init__(start_x, start_y)

        config = ENEMY_TYPES[enemy_type]
        self.enemy_type = enemy_type
        self.max_hp = config["hp"]
        self.hp = self.max_hp
        self.speed = config["speed"]
        self.current_speed = self.speed
        self.gpa_damage = config["gpa_damage"]
        self.ects_reward = config["ects_reward"]
        self.color = config["color"]
        self.name = config["name"]

        self.waypoints = waypoints
        self.waypoint_index = 0
        self.slow_timer = 0.0
        self.reached_end = False
        self.radius = 12

    def take_damage(self, damage: float) -> None:
        """Ontvang schade.

        Args:
            damage: Hoeveelheid schade.
        """
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def apply_slow(self, factor: float, duration: float) -> None:
        """Pas een vertraging toe op de vijand.

        Args:
            factor: Snelheidsfactor (0.5 = halve snelheid).
            duration: Duur van het effect in seconden.
        """
        self.slow_timer = duration
        self.current_speed = self.speed * factor

    def update(self, dt: float) -> None:
        """Beweeg richting het volgende waypoint.

        Args:
            dt: Delta time in seconden.
        """
        if not self.alive or self.reached_end:
            return

        # Update slow effect
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.current_speed = self.speed

        # Beweeg naar het volgende waypoint
        if self.waypoint_index < len(self.waypoints):
            target_x, target_y = self.waypoints[self.waypoint_index]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < 2:
                self.waypoint_index += 1
                if self.waypoint_index >= len(self.waypoints):
                    self.reached_end = True
                    return
            else:
                # Normaliseer en beweeg
                move = self.current_speed * dt
                self.x += (dx / distance) * move
                self.y += (dy / distance) * move

    def draw(self, screen: pygame.Surface) -> None:
        """Teken de vijand met een HP-balk.

        Args:
            screen: Het pygame scherm.
        """
        if not self.alive:
            return

        # Teken de vijand (cirkel)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)

        # HP balk boven de vijand
        bar_width = 24
        bar_height = 4
        bar_x = int(self.x) - bar_width // 2
        bar_y = int(self.y) - self.radius - 8
        hp_ratio = self.hp / self.max_hp

        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))


class Opdracht(Enemy):
    """Standaard vijand. Niets speciaals, maar komt in grote aantallen."""

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("opdracht", waypoints)


class Deadline(Enemy):
    """Snelle vijand die moeilijk te raken is.

    Deadlines versnellen naarmate ze dichter bij het einde komen.
    """

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("deadline", waypoints)

    def update(self, dt: float) -> None:
        """Deadlines worden sneller naarmate ze het einde naderen."""
        super().update(dt)
        if self.alive and not self.reached_end and self.slow_timer <= 0:
            # Hoe dichter bij het einde, hoe sneller
            progress = self.waypoint_index / max(len(self.waypoints), 1)
            self.current_speed = self.speed * (1.0 + progress * 0.5)


class Tentamen(Enemy):
    """Trage maar sterke vijand met veel HP.

    Tentamens hebben een schild dat eerst doorbroken moet worden.
    """

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("tentamen", waypoints)
        self.shield = self.max_hp * 0.3  # 30% extra schild

    def take_damage(self, damage: float) -> None:
        """Schild absorbeert eerst de schade."""
        if self.shield > 0:
            self.shield -= damage
            if self.shield < 0:
                # Resterende schade gaat naar HP
                super().take_damage(-self.shield)
                self.shield = 0
        else:
            super().take_damage(damage)

    def draw(self, screen: pygame.Surface) -> None:
        """Teken tentamen met een schildindicator."""
        super().draw(screen)
        if self.alive and self.shield > 0:
            # Teken schild ring
            pygame.draw.circle(
                screen, (100, 150, 255),
                (int(self.x), int(self.y)),
                self.radius + 4, 2
            )


class Professor(Enemy):
    """Boss vijand. Zeer veel HP, langzaam, maar verwoestend.

    Professors herstellen langzaam HP over tijd.
    """

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("professor", waypoints)
        self.regen_rate = 2.0  # HP per seconde

    def update(self, dt: float) -> None:
        """Professors regenereren HP over tijd."""
        super().update(dt)
        if self.alive:
            self.hp = min(self.hp + self.regen_rate * dt, self.max_hp)

    def draw(self, screen: pygame.Surface) -> None:
        """Teken professor groter dan normale vijanden."""
        if not self.alive:
            return

        # Professor is groter
        big_radius = self.radius + 6
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), big_radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), big_radius, 3)

        # HP balk
        bar_width = 32
        bar_height = 5
        bar_x = int(self.x) - bar_width // 2
        bar_y = int(self.y) - big_radius - 10
        hp_ratio = self.hp / self.max_hp

        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))

        # Naam label
        font = pygame.font.SysFont(None, 18)
        text = font.render("PROF", True, WHITE)
        screen.blit(text, (int(self.x) - text.get_width() // 2, bar_y - 14))
