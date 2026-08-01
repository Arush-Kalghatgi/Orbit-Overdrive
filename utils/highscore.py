import json
import os

HIGHSCORE_FILE = "highscore.json"


def _load_data():
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
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(data, f)
        return True
    except OSError:
        return False


def load_high_score():
    return _load_data()["high_score"]


def save_high_score(score):
    data = _load_data()
    data["high_score"] = int(score)
    return _save_data(data)


def load_last_score():
    return _load_data()["last_score"]


def save_last_score(score):
    data = _load_data()
    data["last_score"] = int(score)
    return _save_data(data)