<p align="center">
  <img src="assets/LOGO.png" alt="Orbit Overdrive" width="160">
</p>

<h1 align="center">Orbit Overdrive</h1>

<p align="center">
  A retro-styled 2D space shooter built with Python and Pygame.<br>
  Procedural rendering, custom particle engine, persistent high scores.
</p>

<p align="center">
  <a href="https://wild-winners-studio.itch.io/orbit-overdrive"><img src="https://img.shields.io/badge/Play_on-itch.io-FA5C5C?style=for-the-badge&logo=itch.io&logoColor=white" alt="Play on itch.io"></a>
</p>

---

## Overview

**Orbit Overdrive** is a fast, juicy, retro-styled space shooter. Pilot your ship through endless waves of asteroids, collect turbo pickups for speed boosts, and chase the highest score you can survive.

Everything in the game — every asteroid, particle, pickup, even the crosshair cursor — is rendered procedurally using Pygame primitives. No sprite sheets, no game engine, no asset store.

- **Genre:** Arcade shooter
- **Platform:** Windows
- **Engine:** Pygame 2.6 (Python 3.12+)
- **Codebase size:** ~2,000 lines of Python

## Features

- **Endless waves** with progressively increasing difficulty
- **Three asteroid types** with distinct damage profiles and point values
- **Turbo mechanic** — drain fuel for 3x world speed, 4x passive score, 2x per-kill score
- **Life pickups** that drop every 2-3 turbo pickups
- **Persistent high scores** via local JSON storage
- **Custom particle engine** — explosions, sparks, hit feedback generated per frame
- **Pixel-perfect rendering** at any window size with proper aspect ratio handling
- **Pause menu** with volume sliders and fullscreen control
- **In-game help screen** with controls reference and scoring breakdown

## Controls

| Action | Keyboard | Mouse |
|---|---|---|
| Move | Arrow keys / WASD | — |
| Shoot | Spacebar | Left click |
| Boost | Shift | Right click |
| Pause | Esc | — |
| Fullscreen | F11 | — |
| Help / How to Play | "?" button on title screen | Click |

## Installation

### Play the latest build

Download the Windows binary from the [itch.io page](https://wild-winners-studio.itch.io/orbit-overdrive). Extract and run `OrbitOverdrive.exe`. No installation required.

### Run from source

Requires **Python 3.12 or later**.

```bash
git clone https://github.com/<your-username>/orbit-overdrive.git
cd orbit-overdrive
pip install -r requirements.txt
python main.py
