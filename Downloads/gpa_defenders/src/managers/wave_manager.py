"""Wave management voor GPA Defenders."""

from src.entities.enemy import (
    Enemy,
    Quiz,
    Huiswerk,
    Aanwezigheid,
    Opdracht,
    Midterm,
    Endterm,
    Professor,
)
from src.settings import ENEMY_TYPES, BALANCE_MODEL_NAME


class WaveManager:
    """Beheert wave-opbouw en wave status met een ronde-budgetmodel."""

    def __init__(
        self,
        waypoints: list[tuple[int, int]],
        wave_pressure_multiplier: float = 1.0,
    ):
        self.waypoints = waypoints
        self.wave = 0
        self.wave_active = False
        self.balance_model = BALANCE_MODEL_NAME
        self.wave_pressure_multiplier = max(0.5, float(wave_pressure_multiplier))

        self.enemy_classes = {
            "quiz": Quiz,
            "huiswerk": Huiswerk,
            "attendance": Aanwezigheid,
            "opdracht": Opdracht,
            "midterm": Midterm,
            "endterm": Endterm,
            "professor": Professor,
        }

    def _delayed_waypoints(self, spawn_offset: int) -> list[tuple[int, int]]:
        """Maak een vertraagde startpositie zodat vijanden gespreid spawnen."""
        return [(self.waypoints[0][0] - spawn_offset, self.waypoints[0][1])] + self.waypoints[:]

    def _is_rush_wave(self, wave: int) -> bool:
        return wave >= 4 and wave % 4 == 0

    def _is_endurance_wave(self, wave: int) -> bool:
        return wave >= 6 and wave % 5 == 0

    def _is_boss_wave(self, wave: int) -> bool:
        return wave >= 10 and wave % 10 == 0

    def _wave_budget(self, wave: int) -> float:
        """RBE-achtige budgetcurve (inspired by Bloons-achtige round pressure)."""
        budget = 14 + wave * 4 + int((wave ** 1.35) * 2.4)
        if wave == 1:
            budget *= 0.82
        elif wave == 2:
            budget *= 0.90
        if self._is_rush_wave(wave):
            budget *= 1.12
        if self._is_endurance_wave(wave):
            budget *= 1.15
        if self._is_boss_wave(wave):
            budget *= 1.25
        budget *= self.wave_pressure_multiplier
        return float(budget)

    def _enemy_types_for_wave(self, wave: int) -> list[str]:
        unlocked: list[str] = []
        for enemy_type, config in ENEMY_TYPES.items():
            if wave >= int(config.get("unlock_wave", 1)):
                unlocked.append(enemy_type)
        return unlocked

    def _type_weights(self, wave: int, unlocked: list[str]) -> dict[str, float]:
        weights = {
            "quiz": max(0.08, 0.58 - 0.055 * (wave - 1)),
            "huiswerk": min(0.34, 0.20 + 0.018 * (wave - 1)),
            "attendance": 0.0 if wave < 3 else min(0.26, 0.14 + 0.014 * (wave - 3)),
            "midterm": 0.0 if wave < 5 else min(0.24, 0.08 + 0.014 * (wave - 5)),
            "endterm": 0.0 if wave < 7 else min(0.20, 0.07 + 0.012 * (wave - 7)),
            "opdracht": 0.0 if wave < 9 else min(0.16, 0.06 + 0.010 * (wave - 9)),
            "professor": 0.0,
        }

        if self._is_rush_wave(wave):
            weights["huiswerk"] *= 1.25
            weights["quiz"] *= 0.85
        if self._is_endurance_wave(wave):
            weights["midterm"] *= 1.20
            weights["endterm"] *= 1.20
            weights["opdracht"] *= 1.15
        if self._is_boss_wave(wave):
            weights["professor"] = 1.0

        return {enemy_type: weights.get(enemy_type, 0.0) for enemy_type in unlocked}

    def _allocate_composition(self, wave: int, budget: float) -> dict[str, int]:
        unlocked = self._enemy_types_for_wave(wave)
        weights = self._type_weights(wave, unlocked)

        counts: dict[str, int] = {}
        remaining = budget

        if self._is_boss_wave(wave) and "professor" in unlocked:
            professor_threat = float(ENEMY_TYPES["professor"].get("threat", 34.0))
            counts["professor"] = 1
            remaining = max(0.0, remaining - professor_threat)

        def try_add(enemy_type: str, amount: int) -> None:
            nonlocal remaining
            if amount <= 0 or enemy_type not in unlocked:
                return
            threat = float(ENEMY_TYPES[enemy_type].get("threat", 1.0))
            affordable = min(amount, int(remaining // threat))
            if affordable <= 0:
                return
            counts[enemy_type] = counts.get(enemy_type, 0) + affordable
            remaining -= affordable * threat

        try_add("quiz", max(2, 8 - wave))
        try_add("attendance", 1 + max(0, (wave - 4) // 6))
        try_add("midterm", 1 + (1 if self._is_endurance_wave(wave) else 0))
        try_add("endterm", 1 + (1 if wave >= 12 else 0))
        try_add("opdracht", 1 + (1 if wave >= 14 and wave % 2 == 0 else 0))

        pool = [e for e in unlocked if e != "professor" and weights.get(e, 0.0) > 0.0]
        total_weight = sum(weights[e] for e in pool)
        budget_for_split = remaining
        if total_weight > 0 and budget_for_split > 0:
            for enemy_type in pool:
                threat = float(ENEMY_TYPES[enemy_type].get("threat", 1.0))
                share_budget = budget_for_split * (weights[enemy_type] / total_weight)
                split_count = int(share_budget // threat)
                try_add(enemy_type, split_count)

        min_seed_quiz = max(2, 9 - wave)
        if "quiz" in unlocked:
            quiz_threat = float(ENEMY_TYPES["quiz"].get("threat", 1.0))
            seed_quiz = min(min_seed_quiz, int(remaining // quiz_threat))
            if seed_quiz > 0:
                counts["quiz"] = counts.get("quiz", 0) + seed_quiz
                remaining -= seed_quiz * quiz_threat

        min_threat = min(float(ENEMY_TYPES[e].get("threat", 1.0)) for e in unlocked)
        while remaining >= min_threat:
            affordable = [
                e
                for e in unlocked
                if e != "professor"
                and float(ENEMY_TYPES[e].get("threat", 1.0)) <= remaining
                and weights.get(e, 0.0) > 0.0
            ]
            if not affordable:
                break

            pick = max(
                affordable,
                key=lambda e: (
                    weights[e] / (1.0 + 0.18 * counts.get(e, 0)),
                    -float(ENEMY_TYPES[e].get("threat", 1.0)),
                ),
            )
            threat = float(ENEMY_TYPES[pick].get("threat", 1.0))
            counts[pick] = counts.get(pick, 0) + 1
            remaining -= threat

        if not counts and unlocked:
            fallback = min(unlocked, key=lambda e: float(ENEMY_TYPES[e].get("threat", 1.0)))
            counts[fallback] = 1

        return counts

    def _build_spawn_sequence(self, counts: dict[str, int], wave: int) -> list[str]:
        if not counts:
            return []

        sequence: list[str] = []
        remaining = dict(counts)

        if remaining.get("professor", 0) > 0:
            sequence.extend(["professor"] * remaining["professor"])
            del remaining["professor"]

        order = sorted(
            remaining.keys(),
            key=lambda enemy_type: ENEMY_TYPES[enemy_type]["speed"],
            reverse=self._is_rush_wave(wave),
        )

        while any(v > 0 for v in remaining.values()):
            for enemy_type in order:
                if remaining.get(enemy_type, 0) <= 0:
                    continue
                sequence.append(enemy_type)
                remaining[enemy_type] -= 1

        return sequence

    def _spawn_spacing_for(self, enemy_type: str, wave: int) -> int:
        threat = float(ENEMY_TYPES[enemy_type].get("threat", 1.0))
        speed = float(ENEMY_TYPES[enemy_type]["speed"])

        spacing = 40
        if self._is_rush_wave(wave):
            spacing = 30
        if threat >= 10:
            spacing += 15
        elif threat >= 6:
            spacing += 9
        elif speed >= 110:
            spacing -= 6
        if enemy_type == "professor":
            spacing += 24
        return max(20, int(spacing))

    def _spawn_enemy(self, enemy_type: str, spawn_offset: int, wave: int) -> Enemy:
        """Maak 1 enemy van type + spawn-offset en pas wave scaling toe."""
        delayed_waypoints = self._delayed_waypoints(spawn_offset)
        enemy = self.enemy_classes[enemy_type](delayed_waypoints)
        self._apply_wave_scaling(enemy, wave)
        return enemy

    def _apply_wave_scaling(self, enemy: Enemy, wave: int) -> None:
        """Schaal enemy stats per wave voor consistente late-game druk."""
        if wave <= 3:
            hp_scale = 1.0 + (wave - 1) * 0.08
        elif wave <= 8:
            hp_scale = 1.16 + (wave - 3) * 0.12
        else:
            hp_scale = 1.76 + (wave - 8) * 0.16

        if self._is_endurance_wave(wave):
            hp_scale *= 1.08
        if self._is_boss_wave(wave):
            hp_scale *= 1.12

        speed_scale = min(1.0 + max(0, wave - 2) * 0.022, 1.58)
        if self._is_rush_wave(wave):
            speed_scale *= 1.12

        reward_scale = 1.0 + max(0, wave - 1) * 0.035
        if self._is_boss_wave(wave):
            reward_scale *= 1.10

        gpa_scale = 1.0 + max(0, wave - 6) * 0.025

        enemy.max_hp = max(1, int(round(enemy.max_hp * hp_scale)))
        enemy.hp = float(enemy.max_hp)
        enemy.speed *= speed_scale
        enemy.current_speed = enemy.speed
        enemy.gpa_damage = round(enemy.gpa_damage * gpa_scale, 2)

        scaled_rewards: dict[str, int] = {}
        for currency, amount in enemy.rewards.items():
            scaled_rewards[currency] = max(1, int(round(amount * reward_scale)))
        enemy.rewards = scaled_rewards
        enemy.energy_reward = enemy.rewards.get("energy", 0)

        if hasattr(enemy, "shield"):
            enemy.shield *= hp_scale
        if hasattr(enemy, "regen_rate"):
            enemy.regen_rate *= 1.0 + max(0, wave - 8) * 0.04

    def spawn_wave(self) -> list[Enemy]:
        """Start een nieuwe wave en retourneer de vijanden."""
        self.wave += 1
        self.wave_active = True

        budget = self._wave_budget(self.wave)
        counts = self._allocate_composition(self.wave, budget)
        sequence = self._build_spawn_sequence(counts, self.wave)

        spawned: list[Enemy] = []
        spawn_offset = 0
        for enemy_type in sequence:
            spawned.append(self._spawn_enemy(enemy_type, spawn_offset, self.wave))
            spawn_offset += self._spawn_spacing_for(enemy_type, self.wave)

        return spawned

    def update_wave_state(self, enemies: list[Enemy]) -> None:
        """Markeer wave als klaar zodra er geen vijanden meer zijn."""
        if self.wave_active and len(enemies) == 0:
            self.wave_active = False
