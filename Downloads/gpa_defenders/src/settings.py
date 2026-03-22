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

# Maps
DEFAULT_MAP_ID = "campus_s"
MAP_DEFINITIONS = {
    "campus_s": {
        "name": "Campus S-Route",
        "waypoint_cells": [(-1, 2), (4, 2), (4, 5), (10, 5), (10, 2), (GRID_COLS, 2)],
        "wave_pressure_multiplier": 1.00,
    },
    "library_rush": {
        "name": "Library Rush",
        "waypoint_cells": [(-1, 4), (5, 4), (5, 2), (9, 2), (9, 4), (GRID_COLS, 4)],
        "wave_pressure_multiplier": 0.94,
    },
    "exam_marathon": {
        "name": "Exam Marathon",
        "waypoint_cells": [
            (-1, 1),
            (2, 1),
            (2, 7),
            (6, 7),
            (6, 2),
            (11, 2),
            (11, 6),
            (GRID_COLS, 6),
        ],
        "wave_pressure_multiplier": 1.10,
    },
}

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
STARTING_ENERGY = 16 * ECONOMY_SCALE
WAVE_CLEAR_ENERGY_BASE = int(0.55 * ECONOMY_SCALE)
WAVE_CLEAR_ENERGY_GROWTH = int(0.28 * ECONOMY_SCALE)

# Balancemodel (geinspireerd door de rondedruk/economiecurve uit Bloons TD).
BALANCE_MODEL_NAME = "bloons_round_pressure"

# Tower definities: (naam, kosten, schade, bereik, vuursnelheid, kleur)
TOWER_TYPES = {
    "coffee": {
        "name": "Koffie",
        "desc": "Goedkoop en betrouwbaar. Schiet cafeïne-projectielen.",
        "cost": 5 * ECONOMY_SCALE,
        "costs": {"energy": 5 * ECONOMY_SCALE},
        "damage": 3.0,
        "range": 120,
        "fire_rate": 1.1,  # schoten per seconde
        "color": BROWN,
        "projectile_color": ORANGE,
        "projectile_speed": 320,
    },
    "study_group": {
        "name": "Studiegroep",
        "desc": "Vertraagt vijanden. Lage schade, maar sterk in combinatie.",
        "cost": 10 * ECONOMY_SCALE,
        "costs": {"energy": 10 * ECONOMY_SCALE},
        "damage": 0.9,
        "range": 108,
        "fire_rate": 0.7,
        "color": BLUE,
        "projectile_color": LIGHT_BLUE,
        "projectile_speed": 215,
        "slow_factor": 0.62,  # vertraagt vijanden
        "slow_duration": 2.4,
    },
    "tutor": {
        "name": "Tutor",
        "desc": "Hoge schade, langzaam. Ideaal tegen sterke vijanden.",
        "cost": 24 * ECONOMY_SCALE,
        "costs": {"energy": 24 * ECONOMY_SCALE},
        "damage": 18.0,
        "range": 170,
        "fire_rate": 0.35,
        "color": DARK_GREEN,
        "projectile_color": GREEN,
        "projectile_speed": 265,
    },
    "energy_drink": {
        "name": "Energy Drink",
        "desc": "Razendsnelle vuursnelheid, maar lage schade per schot.",
        "cost": 12 * ECONOMY_SCALE,
        "costs": {"energy": 12 * ECONOMY_SCALE},
        "damage": 1.1,
        "range": 95,
        "fire_rate": 4.0,
        "color": YELLOW,
        "projectile_color": YELLOW,
        "projectile_speed": 430,
    },
    "chatgpt": {
        "name": "ChatGPT",
        "desc": "Specialist: kan alleen Quiz en Huiswerk targetten.",
        "cost": 20 * ECONOMY_SCALE,
        "costs": {"energy": 20 * ECONOMY_SCALE},
        "damage": 7.5,
        "range": 150,
        "fire_rate": 1.25,
        "color": (90, 220, 210),
        "projectile_color": (120, 250, 230),
        "projectile_speed": 300,
    },
    "pen_paper": {
        "name": "Pen & Paper",
        "desc": "Allround toren. Gemiddelde schade en bereik.",
        "cost": 14 * ECONOMY_SCALE,
        "costs": {"energy": 14 * ECONOMY_SCALE},
        "damage": 5.4,
        "range": 132,
        "fire_rate": 0.95,
        "color": (170, 170, 190),
        "projectile_color": (230, 230, 255),
        "projectile_speed": 275,
    },
    "motivatie": {
        "name": "Motivatie",
        "desc": "Richt alleen op Aanwezigheid. Breekt na 3 waves zonder upgrade.",
        "cost": 15 * ECONOMY_SCALE,
        "costs": {"energy": 15 * ECONOMY_SCALE},
        "damage": 1.4,  # langzaam drainen
        "range": 150,
        "fire_rate": 1.15,
        "color": (255, 120, 170),
        "projectile_color": (255, 170, 210),
        "projectile_speed": 235,
    },
    "hoorcolleges": {
        "name": "Hoorcolleges",
        "desc": "Valt niet aan. Buffed nabijgelegen torens passief.",
        "cost": 26 * ECONOMY_SCALE,  # duur support-bouwwerk
        "costs": {"energy": 26 * ECONOMY_SCALE},
        "damage": 0.0,
        "range": 0,
        "fire_rate": 0.0,
        "color": (255, 210, 90),
        "projectile_color": (255, 210, 90),
        "projectile_speed": 0,
    },
}

# Tower upgrades (backend data-driven; UI can consume later)
TOWER_UPGRADES = {
    "coffee": {},
    "study_group": {},
    "tutor": {},
    "energy_drink": {},
    "pen_paper": {},
    "hoorcolleges": {},
    "chatgpt": {
        "chatgpt_plus": {
            "name": "ChatGPT+",
            "cost": 10 * ECONOMY_SCALE,
            "costs": {"energy": 10 * ECONOMY_SCALE},
            "fire_rate_multiplier": 1.55,
        }
    },
    "motivatie": {
        "lock_in": {
            "name": "Lock-in",
            "cost": 9 * ECONOMY_SCALE,
            "costs": {"energy": 9 * ECONOMY_SCALE},
            "unlock_wave": 3,  # beschikbaar na wave 3
            "efficiency_multiplier": 1.35,  # 135% efficiency
        }
    },
}

# Run-based perks (backend-only; UI/flow kan deze later aanroepen).
PERK_WAVE_INTERVAL = 3
PERK_OFFER_COUNT = 3
PERKS = {
    "focus_mode": {
        "name": "Focus Mode",
        "description": "+8% tower damage.",
        "max_stacks": 3,
        "effects": {"damage_multiplier": 1.08},
    },
    "rapid_revision": {
        "name": "Rapid Revision",
        "description": "+12% vuursnelheid voor alle torens.",
        "max_stacks": 3,
        "effects": {"fire_rate_multiplier": 1.12},
    },
    "scholarship_grant": {
        "name": "Scholarship Grant",
        "description": "-10% bouwkosten.",
        "max_stacks": 2,
        "effects": {"tower_cost_multiplier": 0.90},
    },
    "side_hustle": {
        "name": "Side Hustle",
        "description": "+12% energy rewards op kills.",
        "max_stacks": 3,
        "effects": {"energy_reward_multiplier": 1.12},
    },
    "safe_exam_policy": {
        "name": "Safe Exam Policy",
        "description": "-10% GPA-schade bij leaks.",
        "max_stacks": 2,
        "effects": {"gpa_damage_multiplier": 0.90},
    },
    "projector_overclock": {
        "name": "Projector Overclock",
        "description": "+12% projectile snelheid.",
        "max_stacks": 3,
        "effects": {"projectile_speed_multiplier": 1.12},
    },
    "bonus_budget": {
        "name": "Bonus Budget",
        "description": "Direct +160 energy.",
        "max_stacks": 4,
        "effects": {"instant_energy": int(4.0 * ECONOMY_SCALE)},
    },
}

# Enemy definities: (naam, hp, snelheid, gpa_schade, rewards, kleur)
ENEMY_TYPES = {
    "quiz": {
        "name": "Quiz",
        "hp": 14,
        "speed": 68,
        "gpa_damage": 0.08,
        "rewards": {"energy": int(0.24 * ECONOMY_SCALE)},
        "threat": 1.0,
        "unlock_wave": 1,
        "color": WHITE,
    },
    "huiswerk": {
        "name": "Huiswerk",
        "hp": 11,
        "speed": 118,
        "gpa_damage": 0.13,
        "rewards": {"energy": int(0.3 * ECONOMY_SCALE)},
        "threat": 1.45,
        "unlock_wave": 2,
        "color": RED,
    },
    "attendance": {
        "name": "Aanwezigheid",
        "hp": 28,
        "speed": 58,
        "gpa_damage": 0.16,
        "rewards": {"energy": int(0.42 * ECONOMY_SCALE)},
        "threat": 2.3,
        "unlock_wave": 3,
        "color": (255, 80, 140),
    },
    "opdracht": {
        "name": "Opdracht",
        "hp": 135,
        "speed": 40,
        "gpa_damage": 1.1,
        "rewards": {"energy": int(1.55 * ECONOMY_SCALE)},
        "threat": 11.5,
        "unlock_wave": 9,
        "color": (180, 90, 220),
    },
    "midterm": {
        "name": "Midterm",
        "hp": 70,
        "speed": 36,
        "gpa_damage": 0.55,
        "rewards": {"energy": int(0.95 * ECONOMY_SCALE)},
        "threat": 6.0,
        "unlock_wave": 5,
        "color": ORANGE,
    },
    "endterm": {
        "name": "Endterm",
        "hp": 105,
        "speed": 32,
        "gpa_damage": 0.82,
        "rewards": {"energy": int(1.25 * ECONOMY_SCALE)},
        "threat": 8.8,
        "unlock_wave": 7,
        "color": (200, 110, 60),
    },
    "professor": {
        "name": "Professor",
        "hp": 280,
        "speed": 25,
        "gpa_damage": 1.65,
        "rewards": {"energy": int(4.5 * ECONOMY_SCALE)},
        "threat": 34.0,
        "unlock_wave": 10,
        "color": DARK_GRAY,
    },
}
