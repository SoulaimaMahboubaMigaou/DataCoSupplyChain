"""Persistent administrator account store.

The project ships a single administrator whose credentials used to live only
in ``.env``, which meant any profile change was lost on restart. The account is
therefore persisted next to the prediction history, in ``storage/``, and seeded
once from ``ADMIN_EMAIL`` / ``ADMIN_PASSWORD``.

Only the Argon2 hash is written to disk; the plaintext password is never
stored, logged or returned by the API.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from pwdlib import PasswordHash

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACCOUNT_FILE = Path(
    os.getenv(
        "ADMIN_ACCOUNT_FILE",
        str(PROJECT_ROOT / "storage" / "admin_account.json"),
    )
)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")
MIN_PASSWORD_LENGTH = 10

_lock = RLock()
_hasher = PasswordHash.recommended()


class AccountError(ValueError):
    """Raised when a profile update fails validation."""


def normalize_email(email: str) -> str:
    return str(email or "").strip().lower()


def validate_email(email: str) -> str:
    email = normalize_email(email)

    if not email:
        raise AccountError("L'adresse email est obligatoire.")

    if len(email) > 254 or not EMAIL_PATTERN.match(email):
        raise AccountError("Adresse email invalide.")

    return email


def validate_password(password: str) -> str:
    password = str(password or "")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise AccountError(
            "Le mot de passe doit contenir au moins "
            f"{MIN_PASSWORD_LENGTH} caractères."
        )

    if len(password) > 128:
        raise AccountError("Le mot de passe ne peut pas dépasser 128 caractères.")

    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise AccountError(
            "Le mot de passe doit contenir au moins une lettre et un chiffre."
        )

    return password


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seed() -> dict:
    """Build the first account record from the environment."""
    email = normalize_email(os.getenv("ADMIN_EMAIL", ""))
    password = os.getenv("ADMIN_PASSWORD", "")

    if not email or not password:
        raise RuntimeError(
            "ADMIN_EMAIL and ADMIN_PASSWORD must be configured in .env "
            "to create the administrator account."
        )

    return {
        "email": email,
        "password_hash": _hasher.hash(password),
        "token_version": 1,
        "updated_at": _now(),
    }


def _write(account: dict) -> dict:
    ACCOUNT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACCOUNT_FILE.write_text(
        json.dumps(account, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return account


def _read() -> dict:
    """Return the stored account, creating it on first use."""
    with _lock:
        try:
            account = json.loads(ACCOUNT_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            account = None

        if not isinstance(account, dict) or not account.get("password_hash"):
            return _write(_seed())

        account.setdefault("token_version", 1)
        account.setdefault("updated_at", _now())
        return account


def get_email() -> str:
    return _read()["email"]


def get_token_version() -> int:
    return int(_read()["token_version"])


def public_profile() -> dict:
    """Account data safe to expose through the API (never the hash)."""
    account = _read()
    return {
        "email": account["email"],
        "role": "admin",
        "updated_at": account["updated_at"],
    }


def verify_credentials(email: str, password: str) -> bool:
    account = _read()

    if normalize_email(email) != account["email"]:
        return False

    return verify_password(password)


def verify_password(password: str) -> bool:
    account = _read()

    try:
        return _hasher.verify(str(password or ""), account["password_hash"])
    except Exception:
        # A malformed stored hash must read as "wrong password", not a 500.
        return False


def change_email(new_email: str) -> dict:
    """Persist a new email. Existing tokens keep working (subject is reissued)."""
    new_email = validate_email(new_email)

    with _lock:
        account = _read()

        if account["email"] == new_email:
            raise AccountError("Cette adresse email est déjà la vôtre.")

        account["email"] = new_email
        account["updated_at"] = _now()
        _write(account)

    return public_profile()


def change_password(new_password: str) -> dict:
    """Persist a new password and invalidate every token issued so far."""
    new_password = validate_password(new_password)

    with _lock:
        account = _read()

        if _hasher.verify(new_password, account["password_hash"]):
            raise AccountError(
                "Le nouveau mot de passe doit être différent de l'ancien."
            )

        account["password_hash"] = _hasher.hash(new_password)
        account["token_version"] = int(account["token_version"]) + 1
        account["updated_at"] = _now()
        _write(account)

    return public_profile()
