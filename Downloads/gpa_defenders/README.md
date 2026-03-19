# GPA Defenders 🎓🛡️

Een tower defense game waarin je je GPA verdedigt tegen een eindeloze stroom van opdrachten, tentamens en professors.

## Concept

Je GPA begint op **10.0**. Vijanden (opdrachten, tentamens, deadlines, professors) lopen over een pad richting je GPA. Als ze er doorheen komen, verlagen ze je cijfer. Zakt je GPA onder de **5.5**? Dan ben je gezakt!

Plaats torens (koffie, studiegroepen, tutors, energy drinks) langs het pad om vijanden tegen te houden. Verdien **Energy** door vijanden te verslaan en gebruik die om betere torens te bouwen.

## Hoe te spelen

1. Start het spel: `python main.py`
2. Klik op een vrije plek om een toren te plaatsen
3. Selecteer het type toren uit het menu
4. Overleef zoveel mogelijk waves!

## Controls

- **Muisklik**: Toren plaatsen / selecteren
- **1-4**: Toren type kiezen
- **ESC**: Pauze / Menu
- **SPACE**: Volgende wave starten

## Torens

| Toren | Kosten | Omschrijving |
|-------|--------|-------------|
| ☕ Koffie | 200 Energy | Basis toren, schiet cafeïne |
| 📚 Studiegroep | 400 Energy | Vertraagt vijanden |
| 🎓 Tutor | 800 Energy | Hoge schade, langzaam |
| ⚡ Energy Drink | 600 Energy | Snelle aanval, lage schade |

## Vijanden

| Vijand | HP | Snelheid | Schade aan GPA |
|--------|-----|---------|----------------|
| 📝 Opdracht | Laag | Normaal | -0.1 |
| 📅 Deadline | Laag | Snel | -0.2 |
| 📖 Tentamen | Hoog | Langzaam | -0.5 |
| 👨‍🏫 Professor | Zeer hoog | Langzaam | -1.0 |

## Installatie

```bash
pip install pygame
git clone <repo-url>
cd gpa_defenders
python main.py
```

## Structuur

```
gpa_defenders/
├── main.py                 # Entry point
├── README.md
└── src/
    ├── __init__.py
    ├── settings.py          # Constanten en configuratie
    ├── entities/
    │   ├── __init__.py
    │   ├── entity.py        # Base class
    │   ├── tower.py         # Tower base + subclasses
    │   ├── enemy.py         # Enemy base + subclasses
    │   └── projectile.py    # Projectile base + subclasses
    ├── managers/
    │   ├── __init__.py
    │   ├── game_manager.py  # Hoofdlogica
    │   ├── wave_manager.py  # Wave spawning
    │   └── grid.py          # Grid / map
    └── utils/
        ├── __init__.py
        └── helpers.py       # Hulpfuncties
```

## Team

- [Naam 1] - [Rol]
- [Naam 2] - [Rol]
