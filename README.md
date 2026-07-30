# Orbit Overdrive

A retro-style 2D space shooter built with Pygame. Pilot your spaceship
through waves of asteroids, collect turbo pickups for speed boosts,
survive as long as you can.

![Screenshot](README_screenshot.png)

## Features

- **Custom particle engine** — explosions, sparks, hit feedback
- **Dynamic difficulty** — spawn intervals shorten as your score climbs
- **Fuel-based turbo mechanic** — drain fuel for 3x world speed + score multiplier
- **Persistent high scores** — saved across sessions
- **On-screen touch UI** — auto-shown on web builds, optional on desktop (F10)
- **Mouse or keyboard** — play either way on desktop

## Built With

- **Python 3.12**
- **Pygame 2.6**
- **PyInstaller** (desktop distribution)

## How to Run (From Source)

```bash
pip install -r requirements.txt
python main.py
