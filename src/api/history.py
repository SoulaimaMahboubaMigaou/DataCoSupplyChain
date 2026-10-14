
import json
import os
from pathlib import Path
from threading import Lock

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HISTORY_FILE = Path(
    os.getenv(
        "PREDICTION_HISTORY_FILE",
        str(PROJECT_ROOT / "storage" / "predictions.json"),
    )
)
STORAGE_DIR = HISTORY_FILE.parent
LOCK = Lock()


def read_history():
    with LOCK:
        if not HISTORY_FILE.exists():
            return []

        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []


def add_prediction(item):
    with LOCK:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

        history = []
        if HISTORY_FILE.exists():
            try:
                history = json.loads(
                    HISTORY_FILE.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                history = []

        history.insert(0, item)
        history = history[:500]

        HISTORY_FILE.write_text(
            json.dumps(history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return item


def clear_history():
    with LOCK:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text("[]", encoding="utf-8")
