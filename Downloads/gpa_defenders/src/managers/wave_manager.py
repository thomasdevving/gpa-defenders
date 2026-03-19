"""Wave management voor GPA Defenders."""

from src.entities.enemy import Enemy, Quiz, Huiswerk, Midterm, Endterm, Professor


class WaveManager:
    """Beheert wave-opbouw en wave status."""

    def __init__(self, waypoints: list[tuple[int, int]]):
        self.waypoints = waypoints
        self.wave = 0
        self.wave_active = False

    def spawn_wave(self) -> list[Enemy]:
        """Start een nieuwe wave en retourneer de vijanden."""
        self.wave += 1
        self.wave_active = True
        endterm_only_wave = self.wave >= 5 and self.wave % 3 == 0

        spawned: list[Enemy] = []

        # Simpele wave logica: meer en sterkere vijanden per wave
        for i in range(3 + self.wave * 2):
            # Verschuif de startpositie zodat ze niet allemaal tegelijk spawnen
            delayed_waypoints = [
                (self.waypoints[0][0] - i * 40, self.waypoints[0][1])
            ] + self.waypoints[:]

            if self.wave < 3:
                spawned.append(Quiz(delayed_waypoints))
            elif self.wave < 5:
                if i % 3 == 0:
                    spawned.append(Huiswerk(delayed_waypoints))
                else:
                    spawned.append(Quiz(delayed_waypoints))
            elif self.wave < 8:
                # Sommige waves zijn "Endterm-only" (geen Midterms).
                if endterm_only_wave and i % 5 == 0:
                    spawned.append(Endterm(delayed_waypoints))
                elif i % 7 == 0:
                    spawned.append(Endterm(delayed_waypoints))
                elif i % 5 == 0:
                    spawned.append(Midterm(delayed_waypoints))
                elif i % 3 == 0:
                    spawned.append(Huiswerk(delayed_waypoints))
                else:
                    spawned.append(Quiz(delayed_waypoints))
            else:
                if i == 0:
                    spawned.append(Professor(delayed_waypoints))
                elif endterm_only_wave and i % 4 == 0:
                    spawned.append(Endterm(delayed_waypoints))
                elif i % 6 == 0:
                    spawned.append(Endterm(delayed_waypoints))
                elif i % 4 == 0:
                    spawned.append(Midterm(delayed_waypoints))
                else:
                    spawned.append(Huiswerk(delayed_waypoints))

        return spawned

    def update_wave_state(self, enemies: list[Enemy]) -> None:
        """Markeer wave als klaar zodra er geen vijanden meer zijn."""
        if self.wave_active and len(enemies) == 0:
            self.wave_active = False
