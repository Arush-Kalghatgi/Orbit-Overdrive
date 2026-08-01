# Orbit Overdrive

A retro-styled 2D space shooter built with **Python** and **Pygame**.

Procedural rendering • Custom particle engine • Persistent high scores

 **Play now:** https://wild-winners-studio.itch.io/orbit-overdrive

---

## Screenshots

| | |
|:-:|:-:|
| ![](Screenshot%20(151).png) | ![](Screenshot%20(152).png) |
| ![](Screenshot%20(153).png) | ![](Screenshot%20(154).png) |

<p align="center">
  <img src="Screenshot%20(155).png" width="70%">
</p>

---

# Overview

**Orbit Overdrive** is a fast-paced retro arcade space shooter where survival is everything.

Pilot your ship through endless asteroid waves, collect turbo pickups to push your speed beyond the limit, dodge increasingly dangerous obstacles, and chase the highest score you can survive.

Every visual element in the game—including asteroids, explosions, particles, pickups, UI effects, and even the crosshair—is rendered procedurally using **Pygame primitives**. There are **no sprite sheets, no game engine, and no asset packs**—everything is generated entirely through code.

---

# Features

- Endless gameplay with progressively increasing difficulty
- Three unique asteroid types with different health, damage, and score values
- Turbo mechanic
  - 3× world speed
  - 4× passive score gain
  - 2× score per asteroid destroyed
- Life pickups that spawn every 2–3 turbo pickups
- Persistent high scores using local JSON storage
- Fully custom particle engine for explosions, sparks, and hit effects
- Pixel-perfect rendering at any window size with proper aspect ratio scaling
- Pause menu featuring:
  - Master Volume
  - Music Volume
  - SFX Volume
  - Fullscreen Toggle
- Built-in Help / How to Play screen
- Smooth retro-inspired visuals

---

# Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12+ | Core programming language |
| Pygame 2.6 | Rendering, audio, input, game loop |
| JSON | Persistent high-score storage |

---

# Technical Highlights

- Approximately **2,000 lines** of Python
- Built entirely from scratch using **Pygame**
- Fully procedural rendering (no sprites)
- Custom particle system
- Resolution-independent rendering
- Object-oriented architecture
- Dynamic difficulty progression
- Persistent save system

---

# Controls

| Action | Keyboard | Mouse |
|--------|----------|-------|
| Move | WASD / Arrow Keys | — |
| Shoot | Spacebar | Left Click |
| Turbo Boost | Left Shift | Right Click |
| Pause | Esc | — |
| Fullscreen | F11 | — |
| Help | "?" button on title screen | Click |

---

# Installation

## Play the Latest Build

Download the latest Windows build from itch.io:

https://wild-winners-studio.itch.io/orbit-overdrive

Extract the ZIP file and launch:

```
OrbitOverdrive.exe
```

No installation required.

---

## Run from Source

Requires **Python 3.12** or later.

```bash
git clone https://github.com/Arush-Kalghatgi/orbit-overdrive.git

cd orbit-overdrive

pip install -r requirements.txt

python main.py
```

---

# Project Structure

```
OrbitOverdrive/
│
├── Screenshot (151).png
├── Screenshot (152).png
├── Screenshot (153).png
├── Screenshot (154).png
├── Screenshot (155).png
├── main.py
├── requirements.txt
├── highscores.json
├── README.md
└── ...
```

---

# Planned Features

- More enemy types
- Boss battles
- Additional weapons
- More power-ups
- Achievement system
- Online leaderboards
- Controller support

---

# Developer

Developed by **Arush Kalghatgi**

If you enjoyed the project, consider giving it a ⭐ on GitHub and checking it out on itch.io.

## Support

If you like the project, don't forget to **Star** the repository!

**Play Orbit Overdrive:**  
https://wild-winners-studio.itch.io/orbit-overdrive
