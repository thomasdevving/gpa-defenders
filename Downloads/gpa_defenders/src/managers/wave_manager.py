"""Wave management voor GPA Defenders."""

from src.entities.enemy import (
    Enemy, Quiz, Huiswerk, Aanwezigheid, Opdracht, Midterm, Endterm, Professor
)
from src.settings import ENEMY_TYPES


class WaveManager:
    """Beheert wave-opbouw en wave status."""

    def __init__(self, waypoints: list[tuple[int, int]]):
        self.waypoints = waypoints
        self.wave = 0
        self.wave_active = False

    def _delayed_waypoints(self, spawn_index: int) -> list[tuple[int, int]]:
        """Maak een vertraagde startpositie zodat vijanden gespreid spawnen."""
        return [
            (self.waypoints[0][0] - spawn_index * 40, self.waypoints[0][1])
        ] + self.waypoints[:]

    def _spawn_enemy(
        self, enemy_type: str, spawn_index: int, no_midterm: bool = False
    ) -> Enemy:
        """Maak 1 enemy van type + spawn-index."""
        delayed_waypoints = self._delayed_waypoints(spawn_index)
        enemy_classes = {
            "quiz": Quiz,
            "huiswerk": Huiswerk,
            "attendance": Aanwezigheid,
            "opdracht": Opdracht,
            "midterm": Midterm,
            "endterm": Endterm,
            "professor": Professor,
        }
        enemy = enemy_classes[enemy_type](delayed_waypoints)

        # Zonder midterm moet Endterm dezelfde GPA-schade doen als Opdracht.
        if enemy_type == "endterm" and no_midterm:
            enemy.gpa_damage = ENEMY_TYPES["opdracht"]["gpa_damage"]

        return enemy

    def _build_class_sequence(
        self,
        attendance_count: int,
        huiswerk_count: int,
        include_midterm: bool = False,
        include_endterm: bool = False,
        include_opdracht: bool = False,
    ) -> list[str]:
        """Bouw een klassensequentie: 2x Attendance, daarna 1x Huiswerk."""
        sequence: list[str] = []
        attendance_left = attendance_count
        huiswerk_left = huiswerk_count
        huiswerk_spawned = 0
        midterm_spawned = False

        while attendance_left > 0 or huiswerk_left > 0:
            for _ in range(2):
                if attendance_left > 0:
                    sequence.append("attendance")
                    attendance_left -= 1

            if huiswerk_left > 0:
                sequence.append("huiswerk")
                huiswerk_left -= 1
                huiswerk_spawned += 1

                if include_midterm and not midterm_spawned and huiswerk_spawned == 3:
                    sequence.append("midterm")
                    midterm_spawned = True
                    if include_endterm:
                        sequence.append("endterm")
                        include_endterm = False

        if include_endterm:
            sequence.append("endterm")
        if include_opdracht:
            sequence.append("opdracht")

        return sequence

    def _spawn_first_wave(self) -> list[Enemy]:
        """Scripted wave 1 met twee classes (A/B)."""
        class_a = self._build_class_sequence(
            attendance_count=15,
            huiswerk_count=7,
            include_midterm=True,
            include_endterm=True,
        )
        class_b = self._build_class_sequence(
            attendance_count=15,
            huiswerk_count=7,
            include_opdracht=True,
        )

        # Interleave A en B zodat beide classes door elkaar heen lopen.
        merged_sequence: list[str] = []
        max_len = max(len(class_a), len(class_b))
        for idx in range(max_len):
            if idx < len(class_a):
                merged_sequence.append(class_a[idx])
            if idx < len(class_b):
                merged_sequence.append(class_b[idx])

        spawned: list[Enemy] = []
        for spawn_index, enemy_type in enumerate(merged_sequence):
            spawned.append(self._spawn_enemy(enemy_type, spawn_index))

        return spawned

    def spawn_wave(self) -> list[Enemy]:
        """Start een nieuwe wave en retourneer de vijanden."""
        self.wave += 1
        self.wave_active = True
        if self.wave == 1:
            return self._spawn_first_wave()

        endterm_only_wave = self.wave >= 5 and self.wave % 3 == 0

        spawned: list[Enemy] = []

        # Simpele wave logica: meer en sterkere vijanden per wave
        for i in range(3 + self.wave * 2):
            if self.wave < 3:
                if self.wave >= 2 and i % 6 == 0:
                    spawned.append(self._spawn_enemy("attendance", i))
                else:
                    spawned.append(self._spawn_enemy("quiz", i))
            elif self.wave < 5:
                if i % 5 == 0:
                    spawned.append(self._spawn_enemy("attendance", i))
                elif i % 3 == 0:
                    spawned.append(self._spawn_enemy("huiswerk", i))
                else:
                    spawned.append(self._spawn_enemy("quiz", i))
            elif self.wave < 8:
                # Sommige waves zijn "Endterm-only" (geen Midterms).
                if endterm_only_wave and i % 5 == 0:
                    spawned.append(self._spawn_enemy("endterm", i, no_midterm=True))
                elif i % 8 == 0:
                    spawned.append(self._spawn_enemy("attendance", i))
                elif i % 7 == 0:
                    spawned.append(
                        self._spawn_enemy("endterm", i, no_midterm=endterm_only_wave)
                    )
                elif i % 5 == 0:
                    spawned.append(self._spawn_enemy("midterm", i))
                elif i % 3 == 0:
                    spawned.append(self._spawn_enemy("huiswerk", i))
                else:
                    spawned.append(self._spawn_enemy("quiz", i))
            else:
                if i == 0:
                    spawned.append(self._spawn_enemy("professor", i))
                elif i % 9 == 0:
                    spawned.append(self._spawn_enemy("attendance", i))
                elif endterm_only_wave and i % 4 == 0:
                    spawned.append(self._spawn_enemy("endterm", i, no_midterm=True))
                elif i % 6 == 0:
                    spawned.append(
                        self._spawn_enemy("endterm", i, no_midterm=endterm_only_wave)
                    )
                elif i % 4 == 0:
                    spawned.append(self._spawn_enemy("midterm", i))
                else:
                    spawned.append(self._spawn_enemy("huiswerk", i))

        return spawned

    def update_wave_state(self, enemies: list[Enemy]) -> None:
        """Markeer wave als klaar zodra er geen vijanden meer zijn."""
        if self.wave_active and len(enemies) == 0:
            self.wave_active = False
