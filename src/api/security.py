
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.api import accounts

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

if len(JWT_SECRET) < 32:
    raise RuntimeError("JWT_SECRET must contain at least 32 characters")

# Creates storage/admin_account.json on first start, seeded from .env.
accounts.get_email()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_admin(email: str, password: str) -> bool:
    return accounts.verify_credentials(email, password)


def create_access_token(subject: str | None = None) -> str:
    """Issue a token for the current administrator.

    The token carries the password version, so every token issued before a
    password change stops being accepted.
    """
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_MINUTES
    )
    payload = {
        "sub": subject or accounts.get_email(),
        "ver": accounts.get_token_version(),
        "exp": expires,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_admin(token: str = Depends(oauth2_scheme)) -> dict:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session invalide ou expirée. Reconnectez-vous.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
    except JWTError:
        raise unauthorized

    subject = accounts.normalize_email(payload.get("sub") or "")

    if not subject or subject != accounts.get_email():
        raise unauthorized

    if int(payload.get("ver", 0)) != accounts.get_token_version():
        raise unauthorized

    return {"email": subject, "role": "admin"}
