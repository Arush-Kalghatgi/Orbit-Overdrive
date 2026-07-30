import json
import os

HIGHSCORE_FILE = "highscore.json"

# Browser-side storage key. Each browser/device is its own sandbox —
# scores are NOT shared across devices. New visitors start at 0.
_STORAGE_KEY = "orbit_overdrive_scores"


def _is_pygbag():
    """True when running inside the Pygbag web runtime (in a browser)."""
    try:
        import platform
        return hasattr(platform, "window") and hasattr(platform, "async_print")
    except ImportError:
        return False


def _pygbag_get(key):
    """Read a string from browser localStorage. Returns None if missing."""
    try:
        import platform
        value = platform.window.localStorage.getItem(key)
        return value if value is not None else None
    except Exception:
        return None


def _pygbag_set(key, value):
    """Write a string to browser localStorage. Silently fails if blocked."""
    try:
        import platform
        platform.window.localStorage.setItem(key, value)
    except Exception:
        pass


def _load_data():
    """Load {"high_score": int, "last_score": int}. Handles browser + desktop."""
    if _is_pygbag():
        raw = _pygbag_get(_STORAGE_KEY)
        if raw:
            try:
                data = json.loads(raw)
                return {
                    "high_score": int(data.get("high_score", 0)),
                    "last_score": int(data.get("last_score", 0)),
                }
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
        # First-ever visit on this browser: scores start at 0.
        return {"high_score": 0, "last_score": 0}

    # Desktop: use a JSON file in the working directory.
    if not os.path.exists(HIGHSCORE_FILE):
        return {"high_score": 0, "last_score": 0}
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            data = json.load(f)
            return {
                "high_score": int(data.get("high_score", 0)),
                "last_score": int(data.get("last_score", 0)),
            }
    except (json.JSONDecodeError, ValueError, OSError):
        return {"high_score": 0, "last_score": 0}


def _save_data(data):
    """Save {"high_score": int, "last_score": int}. Handles browser + desktop."""
    if _is_pygbag():
        try:
            _pygbag_set(_STORAGE_KEY, json.dumps(data))
            return True
        except Exception:
            return False

    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(data, f)
        return True
    except OSError:
        return False


def load_high_score():
    """Load the all-time high score. Returns 0 if missing or corrupted."""
    return _load_data()["high_score"]


def save_high_score(score):
    """Save the high score, keeping the existing last_score intact."""
    data = _load_data()
    data["high_score"] = int(score)
    return _save_data(data)


def load_last_score():
    """Load the score from the most recently finished run."""
    return _load_data()["last_score"]


def save_last_score(score):
    """Save the most recent run's score, keeping the existing high_score intact."""
    data = _load_data()
    data["last_score"] = int(score)
    return _save_data(data)
