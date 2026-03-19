"""Wave management voor GPA Defenders."""

from src.entities.enemy import Enemy, Opdracht, Deadline, Tentamen, Professor


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

        spawned: list[Enemy] = []

        # Simpele wave logica: meer en sterkere vijanden per wave
        for i in range(3 + self.wave * 2):
            # Verschuif de startpositie zodat ze niet allemaal tegelijk spawnen
            delayed_waypoints = [
                (self.waypoints[0][0] - i * 40, self.waypoints[0][1])
            ] + self.waypoints[:]

            if self.wave < 3:
                spawned.append(Opdracht(delayed_waypoints))
            elif self.wave < 5:
                if i % 3 == 0:
                    spawned.append(Deadline(delayed_waypoints))
                else:
                    spawned.append(Opdracht(delayed_waypoints))
            elif self.wave < 8:
                if i % 5 == 0:
                    spawned.append(Tentamen(delayed_waypoints))
                elif i % 3 == 0:
                    spawned.append(Deadline(delayed_waypoints))
                else:
                    spawned.append(Opdracht(delayed_waypoints))
            else:
                if i == 0:
                    spawned.append(Professor(delayed_waypoints))
                elif i % 4 == 0:
                    spawned.append(Tentamen(delayed_waypoints))
                else:
                    spawned.append(Deadline(delayed_waypoints))

        return spawned

    def update_wave_state(self, enemies: list[Enemy]) -> None:
        """Markeer wave als klaar zodra er geen vijanden meer zijn."""
        if self.wave_active and len(enemies) == 0:
            self.wave_active = False
