"""Vijand classes voor GPA Defenders.

Alle vijanden erven van Enemy en hebben uniek gedrag via polymorphism.
"""

import pygame
import math
from src.entities.entity import Entity
from src.settings import ENEMY_TYPES, RED, GREEN, WHITE, BLACK
from src.utils.asset_loader import get_enemy_frame, has_enemy_sprites


class Enemy(Entity):
    """Base class voor alle vijanden.

    Vijanden volgen een pad van waypoints en beschadigen je GPA
    als ze het einde bereiken.

    Attributes:
        enemy_type: Type vijand (quiz, huiswerk, etc.).
        hp: Huidige hitpoints.
        max_hp: Maximale hitpoints.
        speed: Basissnelheid in pixels per seconde.
        current_speed: Huidige snelheid (kan vertraagd zijn).
        gpa_damage: Hoeveel GPA-schade bij het bereiken van het einde.
        energy_reward: Hoeveel energy je krijgt bij het verslaan.
        color: Kleur van de vijand.
        waypoints: Lijst van (x, y) punten om te volgen.
        waypoint_index: Huidige waypoint index.
        slow_timer: Resterende tijd van slow effect.
        active_slow_effects: Actieve slows per tower-id.
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
        self.rewards = config["rewards"]
        self.energy_reward = self.rewards.get("energy", 0)
        self.color = config["color"]
        self.name = config["name"]

        self.waypoints = waypoints
        self.waypoint_index = 0
        self.slow_timer = 0.0
        self.active_slow_effects: dict[int, dict[str, float]] = {}
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

    def _refresh_slow_state(self) -> None:
        """Herbereken totale slow op basis van alle actieve tower-effects."""
        if not self.active_slow_effects:
            self.slow_timer = 0.0
            self.current_speed = self.speed
            return

        combined_factor = 1.0
        max_remaining = 0.0
        for effect in self.active_slow_effects.values():
            combined_factor *= effect["factor"]
            max_remaining = max(max_remaining, effect["remaining"])

        self.slow_timer = max_remaining
        self.current_speed = self.speed * combined_factor

    def apply_slow(
        self,
        factor: float,
        duration: float,
        source_id: int | None = None,
    ) -> None:
        """Pas een vertraging toe op de vijand per tower bron.

        Args:
            factor: Snelheidsfactor (0.5 = halve snelheid).
            duration: Duur van het effect in seconden.
            source_id: Unieke id van de toren die de slow toepast.
        """
        if factor <= 0 or duration <= 0:
            return

        key = -1 if source_id is None else int(source_id)
        existing = self.active_slow_effects.get(key)
        if existing is None:
            self.active_slow_effects[key] = {
                "factor": float(factor),
                "remaining": float(duration),
            }
        else:
            existing["factor"] = min(existing["factor"], float(factor))
            existing["remaining"] = max(existing["remaining"], float(duration))

        self._refresh_slow_state()

    def update(self, dt: float) -> None:
        """Beweeg richting het volgende waypoint.

        Args:
            dt: Delta time in seconden.
        """
        if not self.alive or self.reached_end:
            return

        # Update actieve slows per bron.
        if self.active_slow_effects:
            expired: list[int] = []
            for key, effect in self.active_slow_effects.items():
                effect["remaining"] -= dt
                if effect["remaining"] <= 0:
                    expired.append(key)

            for key in expired:
                del self.active_slow_effects[key]

            self._refresh_slow_state()

        # Beweeg naar waypoints zonder overshoot-oscillatie bij hoge snelheden.
        remaining_move = self.current_speed * dt
        while remaining_move > 0 and self.waypoint_index < len(self.waypoints):
            target_x, target_y = self.waypoints[self.waypoint_index]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            # Al op het waypoint: ga direct naar de volgende.
            if distance == 0:
                self.waypoint_index += 1
                continue

            # Kan deze stap het waypoint halen/voorbijgaan?
            if remaining_move >= distance:
                self.x = target_x
                self.y = target_y
                remaining_move -= distance
                self.waypoint_index += 1
            else:
                # Normaliseer en beweeg een deel van de afstand.
                self.x += (dx / distance) * remaining_move
                self.y += (dy / distance) * remaining_move
                remaining_move = 0

        if self.waypoint_index >= len(self.waypoints):
            self.reached_end = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def draw(self, screen: pygame.Surface) -> None:
        """Teken de vijand met een HP-balk.

        Args:
            screen: Het pygame scherm.
        """
        if not self.alive:
            return

        # Probeer sprite icon te gebruiken
        sprite = get_enemy_frame(self.enemy_type, getattr(self, 'anim_time', 0.0))
        if sprite:
            sz = self.radius * 2
            screen.blit(sprite, (int(self.x) - sz // 2, int(self.y) - sz // 2))
        else:
            # Fallback: cirkel
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


class Quiz(Enemy):
    """Standaard vijand. Niets speciaals, maar komt in grote aantallen."""

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("quiz", waypoints)


class Huiswerk(Enemy):
    """Snelle vijand die moeilijk te raken is.

    Huiswerk versnelt naarmate het dichter bij het einde komt.
    """

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("huiswerk", waypoints)

    def update(self, dt: float) -> None:
        """Huiswerk wordt sneller naarmate het einde nadert."""
        super().update(dt)
        if self.alive and not self.reached_end and self.slow_timer <= 0:
            # Hoe dichter bij het einde, hoe sneller
            progress = self.waypoint_index / max(len(self.waypoints), 1)
            self.current_speed = self.speed * (1.0 + progress * 0.5)


class Aanwezigheid(Enemy):
    """Attendance-vijand. Medium snelheid en HP, stabiele druk op het pad."""

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("attendance", waypoints)


class Opdracht(Enemy):
    """Zware opdracht-vijand met hoge GPA-schade."""

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("opdracht", waypoints)


class Midterm(Enemy):
    """Trage maar sterke vijand met veel HP.

    Midterms hebben een schild dat eerst doorbroken moet worden.
    """

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("midterm", waypoints)
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
        """Teken midterm met een schildindicator."""
        super().draw(screen)
        if self.alive and self.shield > 0:
            # Teken schild ring
            pygame.draw.circle(
                screen, (100, 150, 255),
                (int(self.x), int(self.y)),
                self.radius + 4, 2
            )


class Endterm(Enemy):
    """Zware variant van de Midterm met meer HP en sterker schild."""

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("endterm", waypoints)
        self.shield = self.max_hp * 0.45  # 45% extra schild

    def take_damage(self, damage: float) -> None:
        """Schild absorbeert eerst de schade."""
        if self.shield > 0:
            self.shield -= damage
            if self.shield < 0:
                super().take_damage(-self.shield)
                self.shield = 0
        else:
            super().take_damage(damage)

    def draw(self, screen: pygame.Surface) -> None:
        """Teken endterm met zwaardere schild-visual."""
        super().draw(screen)
        if self.alive and self.shield > 0:
            pygame.draw.circle(
                screen, (180, 120, 255),
                (int(self.x), int(self.y)),
                self.radius + 5, 3
            )


class Professor(Enemy):
    """Boss vijand. Zeer veel HP, langzaam, maar verwoestend.

    Professors herstellen langzaam HP over tijd.
    """

    def __init__(self, waypoints: list[tuple[int, int]]):
        super().__init__("professor", waypoints)
        self.regen_rate = 2.0  # HP per seconde
        self.anim_time = 0.0
        self._facing_right = True

    def update(self, dt: float) -> None:
        """Professors regenereren HP over tijd."""
        old_x = self.x
        super().update(dt)
        if self.alive:
            self.hp = min(self.hp + self.regen_rate * dt, self.max_hp)
            self.anim_time += dt
            # Kijkrichting bepalen
            if self.x > old_x:
                self._facing_right = True
            elif self.x < old_x:
                self._facing_right = False

    def draw(self, screen: pygame.Surface) -> None:
        """Teken professor met geanimeerde sprite of fallback."""
        if not self.alive:
            return

        big_radius = self.radius + 6
        sprite = get_enemy_frame("professor", self.anim_time)
        if sprite:
            # Flip als de professor naar links loopt
            if not self._facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            sz = big_radius * 2 + 4
            screen.blit(sprite, (int(self.x) - sz // 2, int(self.y) - sz // 2))
        else:
            # Fallback: cirkel
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
