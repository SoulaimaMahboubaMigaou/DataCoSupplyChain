from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from src.api import accounts
from src.api.accounts import AccountError
from src.api.security import (
    create_access_token,
    get_current_admin,
    verify_admin,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileResponse(BaseModel):
    email: str
    role: str
    updated_at: str | None = None


class EmailUpdateRequest(BaseModel):
    email: str = Field(max_length=254)
    current_password: str = Field(min_length=1, max_length=128)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=128)


class ProfileUpdateResponse(BaseModel):
    profile: ProfileResponse
    access_token: str
    token_type: str = "bearer"
    message: str


def _check_current_password(current_password: str) -> None:
    if not accounts.verify_password(current_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mot de passe actuel incorrect.",
        )


@router.post("/login", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    if not verify_admin(form.username, form.password):
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect",
        )

    return {"access_token": create_access_token()}


@router.get("/me", response_model=ProfileResponse)
def me(admin: dict = Depends(get_current_admin)):
    return accounts.public_profile()


@router.patch("/me", response_model=ProfileUpdateResponse)
def update_email(
    payload: EmailUpdateRequest,
    admin: dict = Depends(get_current_admin),
):
    """Change the administrator email.

    The current password is required: a stolen token alone must not be enough
    to take over the account. A fresh token is returned because the previous
    one is bound to the former email.
    """
    _check_current_password(payload.current_password)

    try:
        profile = accounts.change_email(payload.email)
    except AccountError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "profile": profile,
        "access_token": create_access_token(),
        "message": "Adresse email mise à jour.",
    }


@router.post("/change-password", response_model=ProfileUpdateResponse)
def change_password(
    payload: PasswordChangeRequest,
    admin: dict = Depends(get_current_admin),
):
    """Change the password and invalidate every session issued before it."""
    _check_current_password(payload.current_password)

    try:
        profile = accounts.change_password(payload.new_password)
    except AccountError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return {
        "profile": profile,
        "access_token": create_access_token(),
        "message": (
            "Mot de passe mis à jour. Les autres sessions ont été déconnectées."
        ),
    }
