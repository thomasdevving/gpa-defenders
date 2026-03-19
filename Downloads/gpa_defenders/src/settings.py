"""Configuratie en constanten voor GPA Defenders."""

# Scherm
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "GPA Defenders 🎓"

# Grid
TILE_SIZE = 64
GRID_COLS = SCREEN_WIDTH // TILE_SIZE
GRID_ROWS = (SCREEN_HEIGHT - 150) // TILE_SIZE  # ruimte voor UI onderaan

# Kleuren
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 200, 50)
ORANGE = (255, 140, 50)
BROWN = (139, 90, 43)
LIGHT_BLUE = (150, 200, 255)
DARK_GREEN = (30, 100, 30)
PATH_COLOR = (210, 180, 140)
GRASS_COLOR = (100, 160, 80)

# GPA
STARTING_GPA = 10.0
FAILING_GPA = 5.5

# Economy
ECONOMY_SCALE = 40
STARTING_ENERGY = 30 * ECONOMY_SCALE

# Tower definities: (naam, kosten, schade, bereik, vuursnelheid, kleur)
TOWER_TYPES = {
    "coffee": {
        "name": "Koffie",
        "cost": 5 * ECONOMY_SCALE,
        "costs": {"energy": 5 * ECONOMY_SCALE},
        "damage": 2,
        "range": 120,
        "fire_rate": 1.0,  # schoten per seconde
        "color": BROWN,
        "projectile_color": ORANGE,
        "projectile_speed": 300,
    },
    "study_group": {
        "name": "Studiegroep",
        "cost": 10 * ECONOMY_SCALE,
        "costs": {"energy": 10 * ECONOMY_SCALE},
        "damage": 1,
        "range": 100,
        "fire_rate": 0.5,
        "color": BLUE,
        "projectile_color": LIGHT_BLUE,
        "projectile_speed": 200,
        "slow_factor": 0.5,  # vertraagt vijanden
        "slow_duration": 2.0,
    },
    "tutor": {
        "name": "Tutor",
        "cost": 20 * ECONOMY_SCALE,
        "costs": {"energy": 20 * ECONOMY_SCALE},
        "damage": 8,
        "range": 150,
        "fire_rate": 0.3,
        "color": DARK_GREEN,
        "projectile_color": GREEN,
        "projectile_speed": 250,
    },
    "energy_drink": {
        "name": "Energy Drink",
        "cost": 15 * ECONOMY_SCALE,
        "costs": {"energy": 15 * ECONOMY_SCALE},
        "damage": 1,
        "range": 100,
        "fire_rate": 3.0,
        "color": YELLOW,
        "projectile_color": YELLOW,
        "projectile_speed": 400,
    },
}

# Enemy definities: (naam, hp, snelheid, gpa_schade, rewards, kleur)
ENEMY_TYPES = {
    "quiz": {
        "name": "Quiz",
        "hp": 10,
        "speed": 60,
        "gpa_damage": 0.1,
        "rewards": {"energy": 3 * ECONOMY_SCALE},
        "color": WHITE,
    },
    "huiswerk": {
        "name": "Huiswerk",
        "hp": 8,
        "speed": 120,
        "gpa_damage": 0.2,
        "rewards": {"energy": 5 * ECONOMY_SCALE},
        "color": RED,
    },
    "midterm": {
        "name": "Midterm",
        "hp": 40,
        "speed": 35,
        "gpa_damage": 0.5,
        "rewards": {"energy": 10 * ECONOMY_SCALE},
        "color": ORANGE,
    },
    "endterm": {
        "name": "Endterm",
        "hp": 65,
        "speed": 30,
        "gpa_damage": 0.8,
        "rewards": {"energy": 14 * ECONOMY_SCALE},
        "color": (200, 110, 60),
    },
    "professor": {
        "name": "Professor",
        "hp": 100,
        "speed": 25,
        "gpa_damage": 1.0,
        "rewards": {"energy": 25 * ECONOMY_SCALE},
        "color": DARK_GRAY,
    },
}
