"""Core game-state updates voor GPA Defenders."""

from typing import TYPE_CHECKING

from src.entities.projectile import Projectile
from src.entities.tower import create_tower
from src.settings import (
    STARTING_GPA, STARTING_ENERGY, FAILING_GPA, TOWER_TYPES
)

if TYPE_CHECKING:
    from src.managers.grid import GridMap
    from src.managers.wave_manager import WaveManager


class GameManager:
    """Beheert combat, resources en verliesconditie."""

    def __init__(self):
        self.gpa = STARTING_GPA
        self.currencies = {"energy": STARTING_ENERGY}
        self.game_over = False
        self.allowed_speeds = (1.0, 2.0, 4.0)
        self.speed_multiplier = 1.0

        self.towers: list = []
        self.enemies: list = []
        self.projectiles: list = []
        self.hoorcolleges_damage_multiplier = 1.25
        self.hoorcolleges_motivatie_discount = 0.25

    @property
    def energy(self) -> int:
        return self.currencies["energy"]

    @energy.setter
    def energy(self, value: int) -> None:
        self.currencies["energy"] = max(0, int(value))

    def set_speed(self, multiplier: float) -> None:
        """Zet de gamesnelheid op 1x, 2x of 4x."""
        if multiplier not in self.allowed_speeds:
            raise ValueError(
                f"Ongeldige snelheid: {multiplier}. Toegestaan: {self.allowed_speeds}"
            )
        self.speed_multiplier = multiplier

    def cycle_speed(self) -> float:
        """Cycle door 1x -> 2x -> 4x -> 1x en return de nieuwe waarde."""
        idx = self.allowed_speeds.index(self.speed_multiplier)
        self.speed_multiplier = self.allowed_speeds[(idx + 1) % len(self.allowed_speeds)]
        return self.speed_multiplier

    def get_currency(self, currency: str) -> int:
        """Geef het huidige saldo van een currency."""
        return self.currencies.get(currency, 0)

    def add_currency(self, currency: str, amount: int) -> None:
        """Voeg currency toe (of trek af bij negatieve amount)."""
        current = self.get_currency(currency)
        self.currencies[currency] = max(0, current + int(amount))

    def can_afford_costs(self, costs: dict[str, int]) -> bool:
        """Check of alle benodigde currencies beschikbaar zijn."""
        return all(self.get_currency(cur) >= amount for cur, amount in costs.items())

    def spend_costs(self, costs: dict[str, int]) -> bool:
        """Probeer een costs-pakket af te schrijven."""
        if not self.can_afford_costs(costs):
            return False
        for cur, amount in costs.items():
            self.add_currency(cur, -amount)
        return True

    def can_afford_tower(self, tower_type: str) -> bool:
        """Check of de speler genoeg resources heeft voor een toren."""
        costs = self.get_tower_costs(tower_type)
        return self.can_afford_costs(costs)

    def has_tower_type(self, tower_type: str) -> bool:
        """Check of er al minstens 1 toren van dit type geplaatst is."""
        return any(t.tower_type == tower_type for t in self.towers)

    def get_tower_costs(self, tower_type: str) -> dict[str, int]:
        """Geef effectieve kosten terug (inclusief eventuele kortingen)."""
        config = TOWER_TYPES[tower_type]
        costs = dict(config.get("costs", {"energy": config["cost"]}))

        if tower_type == "hoorcolleges" and self.has_tower_type("motivatie"):
            energy = costs.get("energy", 0)
            discounted = int(round(energy * (1.0 - self.hoorcolleges_motivatie_discount)))
            costs["energy"] = max(1, discounted)

        return costs

    def get_damage_multiplier(self) -> float:
        """Globale damage multiplier door support towers."""
        if self.has_tower_type("hoorcolleges"):
            return self.hoorcolleges_damage_multiplier
        return 1.0

    def place_tower(self, tower_type: str, grid_x: int, grid_y: int) -> bool:
        """Plaats een toren als de speler genoeg resources heeft."""
        costs = self.get_tower_costs(tower_type)
        if not self.spend_costs(costs):
            return False

        tower = create_tower(tower_type, grid_x, grid_y)
        # Bewaar de effectief betaalde kost (belangrijk voor refund bij verkoop).
        tower.costs = dict(costs)
        tower.energy_cost = costs.get("energy", tower.energy_cost)
        tower.cost = tower.energy_cost
        self.towers.append(tower)
        return True

    def get_tower_at(self, grid_x: int, grid_y: int):
        """Zoek een toren op grid positie."""
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return tower
        return None

    def sell_tower_at(self, grid_x: int, grid_y: int, grid_map: "GridMap") -> int:
        """Verkoop toren op een cel en geef 75% van de kost terug.

        Returns:
            Teruggegeven energy. 0 als er geen toren op die cel staat.
        """
        tower = self.get_tower_at(grid_x, grid_y)
        if tower is None:
            return 0

        refund = int(tower.energy_cost * 0.75)
        self.towers.remove(tower)
        grid_map.remove_tower(grid_x, grid_y)
        self.add_currency("energy", refund)
        return refund

    def add_enemies(self, enemies: list) -> None:
        """Voeg een batch vijanden toe aan het speelveld."""
        self.enemies.extend(enemies)

    def update(self, dt: float, wave_manager: "WaveManager") -> None:
        """Update combat, rewards, wave status en fail condition."""
        if self.game_over:
            return
        scaled_dt = dt * self.speed_multiplier
        # Motivatie buff: energy rewards op 130% als er minstens 1 Motivatie-toren staat.
        energy_reward_multiplier = (
            1.3 if any(t.tower_type == "motivatie" for t in self.towers) else 1.0
        )

        # Update torens en maak projectielen
        damage_multiplier = self.get_damage_multiplier()
        for tower in self.towers:
            result = tower.update(scaled_dt, self.enemies)
            if result:
                result["damage"] *= damage_multiplier
                proj = Projectile(
                    result["x"], result["y"], result["target"],
                    result["damage"], result["speed"], result["color"],
                    result.get("slow_factor", 0), result.get("slow_duration", 0),
                )
                self.projectiles.append(proj)

        # Update vijanden
        for enemy in self.enemies:
            enemy.update(scaled_dt)
            if enemy.reached_end:
                self.gpa -= enemy.gpa_damage
                enemy.alive = False

        # Update projectielen
        for proj in self.projectiles:
            proj.update(scaled_dt)

        # Reward voor kills (niet voor enemies die het einde halen).
        for enemy in self.enemies:
            if not enemy.alive and not enemy.reached_end:
                for currency, amount in enemy.rewards.items():
                    if currency == "energy":
                        amount = int(amount * energy_reward_multiplier)
                    self.add_currency(currency, amount)

        # Verwijder dode objecten
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Check wave klaar
        wave_manager.update_wave_state(self.enemies)

        # Check game over
        if self.gpa <= FAILING_GPA:
            self.game_over = True
