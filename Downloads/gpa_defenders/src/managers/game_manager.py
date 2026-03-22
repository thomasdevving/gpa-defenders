"""Core game-state updates voor GPA Defenders."""

import random
from typing import TYPE_CHECKING

from src.entities.projectile import Projectile
from src.entities.tower import create_tower
from src.settings import (
    STARTING_GPA,
    STARTING_ENERGY,
    FAILING_GPA,
    TOWER_TYPES,
    TOWER_UPGRADES,
    WAVE_CLEAR_ENERGY_BASE,
    WAVE_CLEAR_ENERGY_GROWTH,
    PERKS,
    PERK_WAVE_INTERVAL,
    PERK_OFFER_COUNT,
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
        self.hoorcolleges_damage_multiplier = 1.18
        self.hoorcolleges_motivatie_discount = 0.25
        self.pen_paper_coffee_adjacent_fire_rate_boost = 0.20
        self.hoorcolleges_no_motivatie_efficiency = 0.65
        self.motivatie_repair_cost_factor = 0.40
        self.motivatie_energy_reward_multiplier = 1.15

        # Run-based perk state
        self.perk_rng = random.Random()
        self.pending_perk_choices: list[dict] = []
        self.applied_perks: list[str] = []
        self.perk_stacks: dict[str, int] = {}
        self.global_damage_multiplier = 1.5
        self.global_fire_rate_multiplier = 1.0
        self.global_tower_cost_multiplier = 1.0
        self.global_energy_reward_multiplier = 1.25
        self.global_gpa_damage_multiplier = 1.0
        self.global_projectile_speed_multiplier = 1.0
        self.wave_clear_bonus_multiplier = 1.0

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

    def has_active_tower_type(self, tower_type: str) -> bool:
        """Check of er minstens 1 actief (niet-broken) tower-type is."""
        return any(
            t.tower_type == tower_type and not getattr(t, "is_broken", False)
            for t in self.towers
        )

    def get_tower_costs(self, tower_type: str) -> dict[str, int]:
        """Geef effectieve kosten terug (inclusief eventuele kortingen)."""
        config = TOWER_TYPES[tower_type]
        costs = dict(config.get("costs", {"energy": config["cost"]}))

        if tower_type == "hoorcolleges" and self.has_tower_type("motivatie"):
            energy = costs.get("energy", 0)
            discounted = int(round(energy * (1.0 - self.hoorcolleges_motivatie_discount)))
            costs["energy"] = max(1, discounted)

        for cur, amount in list(costs.items()):
            costs[cur] = max(1, int(round(amount * self.global_tower_cost_multiplier)))

        return costs

    def get_upgrade_config(self, tower_type: str, upgrade_id: str) -> dict | None:
        """Haal upgradeconfig op voor een torentype."""
        return TOWER_UPGRADES.get(tower_type, {}).get(upgrade_id)

    def get_tower_upgrades(self, tower_type: str) -> dict[str, dict]:
        """Alle gedefinieerde upgrades voor een torentype."""
        return TOWER_UPGRADES.get(tower_type, {})

    def can_upgrade_tower(
        self, tower, upgrade_id: str, current_wave: int, wave_active: bool = False
    ) -> bool:
        """Check of een bestaande toren geupgrade kan worden."""
        upgrade = self.get_upgrade_config(tower.tower_type, upgrade_id)
        if upgrade is None or tower.has_upgrade(upgrade_id):
            return False

        unlock_wave = int(upgrade.get("unlock_wave", 0))
        if current_wave < unlock_wave:
            return False
        if current_wave == unlock_wave and wave_active:
            return False

        costs = dict(upgrade.get("costs", {"energy": upgrade["cost"]}))
        return self.can_afford_costs(costs)

    def upgrade_tower_at(
        self, grid_x: int, grid_y: int, upgrade_id: str,
        current_wave: int, wave_active: bool = False
    ) -> bool:
        """Voer een toren-upgrade uit op een gridpositie."""
        tower = self.get_tower_at(grid_x, grid_y)
        if tower is None:
            return False

        if not self.can_upgrade_tower(tower, upgrade_id, current_wave, wave_active):
            return False

        upgrade = self.get_upgrade_config(tower.tower_type, upgrade_id)
        costs = dict(upgrade.get("costs", {"energy": upgrade["cost"]}))
        if not self.spend_costs(costs):
            return False

        return tower.apply_upgrade(upgrade_id, upgrade)

    def get_damage_multiplier(self) -> float:
        """Globale damage multiplier door support towers."""
        if self.has_tower_type("hoorcolleges"):
            bonus = self.hoorcolleges_damage_multiplier - 1.0
            if not self.has_active_tower_type("motivatie"):
                bonus *= self.hoorcolleges_no_motivatie_efficiency
            return 1.0 + bonus
        return 1.0

    def get_repair_costs(self, tower_type: str) -> dict[str, int]:
        """Geef repairkosten voor een torentype."""
        base_cost = int(round(TOWER_TYPES[tower_type]["cost"] * self.global_tower_cost_multiplier))
        return {"energy": max(1, int(base_cost * self.motivatie_repair_cost_factor))}

    def can_repair_tower_at(self, grid_x: int, grid_y: int) -> bool:
        """Check of er een kapotte reparabele toren staat en je kan betalen."""
        tower = self.get_tower_at(grid_x, grid_y)
        if tower is None:
            return False
        if tower.tower_type != "motivatie":
            return False
        if not getattr(tower, "is_broken", False):
            return False
        costs = self.get_repair_costs(tower.tower_type)
        return self.can_afford_costs(costs)

    def repair_tower_at(self, grid_x: int, grid_y: int) -> bool:
        """Repareer een kapotte Motivatie-toren voor halve basiskost."""
        tower = self.get_tower_at(grid_x, grid_y)
        if tower is None:
            return False
        if tower.tower_type != "motivatie":
            return False
        if not getattr(tower, "is_broken", False):
            return False

        costs = self.get_repair_costs(tower.tower_type)
        if not self.spend_costs(costs):
            return False

        tower.repair()
        return True

    def get_wave_clear_bonus(self, wave: int) -> int:
        """Geef de vaste energy-bonus na het clearen van een wave."""
        bonus = WAVE_CLEAR_ENERGY_BASE + max(0, wave - 1) * WAVE_CLEAR_ENERGY_GROWTH
        bonus *= self.wave_clear_bonus_multiplier
        return max(0, int(bonus))

    def has_pending_perk_choice(self) -> bool:
        """True als er een perk-keuze openstaat."""
        return len(self.pending_perk_choices) > 0

    def get_pending_perk_choices(self) -> list[dict]:
        """Read-only snapshot van de huidige perk opties."""
        return [dict(choice) for choice in self.pending_perk_choices]

    def _available_perk_ids(self) -> list[str]:
        """Perks die nog stacks over hebben."""
        available: list[str] = []
        for perk_id, config in PERKS.items():
            current = self.perk_stacks.get(perk_id, 0)
            max_stacks = int(config.get("max_stacks", 1))
            if current < max_stacks:
                available.append(perk_id)
        return available

    def _perk_snapshot(self, perk_id: str) -> dict:
        """UI-agnostische perk payload."""
        config = PERKS[perk_id]
        current = self.perk_stacks.get(perk_id, 0)
        max_stacks = int(config.get("max_stacks", 1))
        return {
            "id": perk_id,
            "name": config["name"],
            "description": config["description"],
            "current_stacks": current,
            "max_stacks": max_stacks,
            "next_stack": current + 1,
        }

    def offer_perks(self, wave: int) -> list[dict]:
        """Genereer een perk-aanbod (typisch na elke Nde wave)."""
        if wave <= 0 or wave % PERK_WAVE_INTERVAL != 0:
            return []
        if self.has_pending_perk_choice():
            return self.get_pending_perk_choices()

        available = self._available_perk_ids()
        if not available:
            self.pending_perk_choices = []
            return []

        k = min(PERK_OFFER_COUNT, len(available))
        selected_ids = self.perk_rng.sample(available, k)
        self.pending_perk_choices = [self._perk_snapshot(perk_id) for perk_id in selected_ids]
        return self.get_pending_perk_choices()

    def _apply_perk_effects(self, effects: dict) -> None:
        """Pas de effecten van een perk stack toe."""
        damage_mul = effects.get("damage_multiplier")
        if damage_mul is not None:
            self.global_damage_multiplier *= float(damage_mul)

        fire_rate_mul = effects.get("fire_rate_multiplier")
        if fire_rate_mul is not None:
            self.global_fire_rate_multiplier *= float(fire_rate_mul)

        tower_cost_mul = effects.get("tower_cost_multiplier")
        if tower_cost_mul is not None:
            self.global_tower_cost_multiplier *= float(tower_cost_mul)

        energy_reward_mul = effects.get("energy_reward_multiplier")
        if energy_reward_mul is not None:
            self.global_energy_reward_multiplier *= float(energy_reward_mul)

        gpa_damage_mul = effects.get("gpa_damage_multiplier")
        if gpa_damage_mul is not None:
            self.global_gpa_damage_multiplier *= float(gpa_damage_mul)

        projectile_speed_mul = effects.get("projectile_speed_multiplier")
        if projectile_speed_mul is not None:
            self.global_projectile_speed_multiplier *= float(projectile_speed_mul)

        wave_bonus_mul = effects.get("wave_clear_bonus_multiplier")
        if wave_bonus_mul is not None:
            self.wave_clear_bonus_multiplier *= float(wave_bonus_mul)

        instant_energy = effects.get("instant_energy")
        if instant_energy is not None:
            self.add_currency("energy", int(instant_energy))

    def apply_perk(self, perk_id: str) -> bool:
        """Apply 1 perk stack (bij voorkeur een optie uit pending_perk_choices)."""
        if perk_id not in PERKS:
            return False

        if self.has_pending_perk_choice():
            offered_ids = {choice["id"] for choice in self.pending_perk_choices}
            if perk_id not in offered_ids:
                return False

        config = PERKS[perk_id]
        current = self.perk_stacks.get(perk_id, 0)
        max_stacks = int(config.get("max_stacks", 1))
        if current >= max_stacks:
            return False

        self._apply_perk_effects(config.get("effects", {}))
        self.perk_stacks[perk_id] = current + 1
        self.applied_perks.append(perk_id)
        self.pending_perk_choices = []
        return True

    def _handle_wave_completed(self, wave: int) -> None:
        """Wave-complete hooks voor towers plus wave-clear economy."""
        self.add_currency("energy", self.get_wave_clear_bonus(wave))
        self.offer_perks(wave)
        for tower in self.towers:
            if tower.tower_type == "motivatie" and hasattr(tower, "on_wave_completed"):
                tower.on_wave_completed()

    def _has_adjacent_tower_type(self, tower, neighbor_type: str) -> bool:
        """Check 4-richtings-adjacentie op basis van grid-posities."""
        neighbor_offsets = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for dx, dy in neighbor_offsets:
            nx = tower.grid_x + dx
            ny = tower.grid_y + dy
            neighbor = self.get_tower_at(nx, ny)
            if neighbor and neighbor.tower_type == neighbor_type:
                return True
        return False

    def _recalculate_tower_synergies(self) -> None:
        """Herbereken stat-buffs die afhangen van plaatsing/layout."""
        for tower in self.towers:
            if tower.tower_type != "pen_paper":
                continue

            fire_rate = tower.base_fire_rate
            if self._has_adjacent_tower_type(tower, "coffee"):
                fire_rate *= (1.0 + self.pen_paper_coffee_adjacent_fire_rate_boost)
            tower.fire_rate = fire_rate

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
        self._recalculate_tower_synergies()
        return True

    def get_tower_at(self, grid_x: int, grid_y: int):
        """Zoek een toren op grid positie."""
        for tower in self.towers:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return tower
        return None

    def sell_tower_at(self, grid_x: int, grid_y: int, grid_map: "GridMap") -> int:
        """Verkoop toren op een cel en geef 70% van de kost terug.

        Returns:
            Teruggegeven energy. 0 als er geen toren op die cel staat.
        """
        tower = self.get_tower_at(grid_x, grid_y)
        if tower is None:
            return 0

        refund = int(tower.energy_cost * 0.70)
        self.towers.remove(tower)
        self._recalculate_tower_synergies()
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
        # Motivatie buff: licht hogere energy rewards zolang er minstens 1 actief is.
        energy_reward_multiplier = (
            self.motivatie_energy_reward_multiplier
            if self.has_active_tower_type("motivatie")
            else 1.0
        )
        energy_reward_multiplier *= self.global_energy_reward_multiplier
        was_wave_active = wave_manager.wave_active

        # Update torens en maak projectielen
        damage_multiplier = self.get_damage_multiplier() * self.global_damage_multiplier
        for tower in self.towers:
            result = tower.update(scaled_dt * self.global_fire_rate_multiplier, self.enemies)
            if result:
                result["damage"] *= damage_multiplier
                proj = Projectile(
                    result["x"], result["y"], result["target"],
                    result["damage"],
                    result["speed"] * self.global_projectile_speed_multiplier,
                    result["color"],
                    result.get("slow_factor", 0),
                    result.get("slow_duration", 0),
                    result.get("slow_source_id"),
                )
                self.projectiles.append(proj)

        # Update vijanden
        for enemy in self.enemies:
            enemy.update(scaled_dt)
            if enemy.reached_end:
                self.gpa -= enemy.gpa_damage * self.global_gpa_damage_multiplier
                enemy.alive = False

        # Update projectielen
        for proj in self.projectiles:
            proj.update(scaled_dt)

        # Reward voor kills (niet voor enemies die het einde halen).
        for enemy in self.enemies:
            if not enemy.alive and not enemy.reached_end:
                for currency, amount in enemy.rewards.items():
                    if currency == "energy":
                        amount = int(round(amount * energy_reward_multiplier))
                    self.add_currency(currency, amount)

        # Verwijder dode objecten
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Check wave klaar
        wave_manager.update_wave_state(self.enemies)
        if was_wave_active and not wave_manager.wave_active:
            self._handle_wave_completed(wave_manager.wave)

        # Check game over
        if self.gpa <= FAILING_GPA:
            self.game_over = True
