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

# Startgeld
STARTING_ECTS = 30

# Tower definities: (naam, kosten, schade, bereik, vuursnelheid, kleur)
TOWER_TYPES = {
    "coffee": {
        "name": "Koffie",
        "cost": 5,
        "damage": 2,
        "range": 120,
        "fire_rate": 1.0,  # schoten per seconde
        "color": BROWN,
        "projectile_color": ORANGE,
        "projectile_speed": 300,
    },
    "study_group": {
        "name": "Studiegroep",
        "cost": 10,
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
        "cost": 20,
        "damage": 8,
        "range": 150,
        "fire_rate": 0.3,
        "color": DARK_GREEN,
        "projectile_color": GREEN,
        "projectile_speed": 250,
    },
    "energy_drink": {
        "name": "Energy Drink",
        "cost": 15,
        "damage": 1,
        "range": 100,
        "fire_rate": 3.0,
        "color": YELLOW,
        "projectile_color": YELLOW,
        "projectile_speed": 400,
    },
}

# Enemy definities: (naam, hp, snelheid, gpa_schade, ects_beloning, kleur)
ENEMY_TYPES = {
    "opdracht": {
        "name": "Opdracht",
        "hp": 10,
        "speed": 60,
        "gpa_damage": 0.1,
        "ects_reward": 3,
        "color": WHITE,
    },
    "deadline": {
        "name": "Deadline",
        "hp": 8,
        "speed": 120,
        "gpa_damage": 0.2,
        "ects_reward": 5,
        "color": RED,
    },
    "tentamen": {
        "name": "Tentamen",
        "hp": 40,
        "speed": 35,
        "gpa_damage": 0.5,
        "ects_reward": 10,
        "color": ORANGE,
    },
    "professor": {
        "name": "Professor",
        "hp": 100,
        "speed": 25,
        "gpa_damage": 1.0,
        "ects_reward": 25,
        "color": DARK_GRAY,
    },
}
