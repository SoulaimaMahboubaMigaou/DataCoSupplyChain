"""Resolve order destinations to map coordinates.

The DataCo dataset only carries the customer (origin) latitude/longitude, so
the destination city has to be geocoded. Lookups go through Nominatim and are
cached on disk, which keeps repeated searches instant, keeps the API usable
offline once a city is known, and respects the Nominatim usage policy.
"""

import json
import os
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_PATH = ROOT / "storage" / "geocode_cache.json"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "DataCo-SupplyChain-Tracking/1.0"
REQUEST_TIMEOUT = 5
MIN_REQUEST_INTERVAL = 1.1  # Nominatim allows one request per second.

# Set GEOCODING_ENABLED=0 to stay fully offline: cached cities still resolve.
NETWORK_ENABLED = os.getenv("GEOCODING_ENABLED", "1").strip().lower() not in {
    "0", "false", "no", "off",
}

_lock = threading.Lock()
_cache = None
_last_request_at = 0.0


def _load_cache() -> dict:
    global _cache

    if _cache is None:
        try:
            _cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _cache = {}

    return _cache


def _save_cache() -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(
            json.dumps(_cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        # A read-only storage directory must not break tracking.
        pass


def _clean(part) -> str:
    if part is None:
        return ""

    text = str(part).strip()

    # Some rows carry mojibake from the original export (for example
    # "Rajast�n"); those characters only confuse the geocoder.
    if "�" in text:
        text = text.replace("�", "")

    return text.strip(" ,")


def _queries(city: str, state: str, country: str) -> list:
    """Progressively broader queries, from most to least precise."""
    candidates = [
        [city, state, country],
        [city, country],
        [state, country],
        [country],
    ]

    queries = []
    for parts in candidates:
        query = ", ".join(part for part in parts if part)
        if query and query not in queries:
            queries.append(query)

    return queries


def _request(query: str):
    global _last_request_at

    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "limit": 1,
    })
    request = urllib.request.Request(
        f"{NOMINATIM_URL}?{params}",
        headers={"User-Agent": USER_AGENT},
    )

    wait = MIN_REQUEST_INTERVAL - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            results = json.loads(response.read())
    except Exception:
        # No network, timeout, rate limit: the caller falls back gracefully.
        return None
    finally:
        _last_request_at = time.monotonic()

    if not results:
        return None

    try:
        return {
            "lat": float(results[0]["lat"]),
            "lon": float(results[0]["lon"]),
        }
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def geocode(city=None, state=None, country=None, allow_network: bool = True):
    """Return {"lat": float, "lon": float} for a place, or None.

    Cached answers are returned without any network call. A negative answer is
    cached as well so a city that cannot be resolved is not queried on every
    request.
    """
    city, state, country = _clean(city), _clean(state), _clean(country)

    if not (city or country):
        return None

    key = "|".join([city.lower(), state.lower(), country.lower()])

    with _lock:
        cache = _load_cache()

        if key in cache:
            return cache[key]

        if not (allow_network and NETWORK_ENABLED):
            return None

        point = None
        for query in _queries(city, state, country):
            point = _request(query)
            if point is not None:
                break

        cache[key] = point
        _save_cache()

        return point
