"""Authentication and administrator profile tests."""

from tests.conftest import SEED_EMAIL, SEED_PASSWORD

NEW_PASSWORD = "AnotherPassw0rd"
PROTECTED = [
    ("get", "/auth/me"),
    ("get", "/tracking/summary"),
    ("get", "/tracking/shipments"),
    ("post", "/predictions/75939"),
]


def test_login_returns_a_bearer_token(client):
    response = client.post(
        "/auth/login",
        data={"username": SEED_EMAIL, "password": SEED_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_is_case_insensitive_on_email(client):
    response = client.post(
        "/auth/login",
        data={"username": SEED_EMAIL.upper(), "password": SEED_PASSWORD},
    )

    assert response.status_code == 200


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/auth/login",
        data={"username": SEED_EMAIL, "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/auth/login",
        data={"username": "someone@else.com", "password": SEED_PASSWORD},
    )

    assert response.status_code == 401


def test_protected_routes_require_a_token(client):
    for method, path in PROTECTED:
        response = getattr(client, method)(path)
        assert response.status_code == 401, path


def test_protected_routes_reject_a_forged_token(client):
    headers = {"Authorization": "Bearer not.a.jwt"}

    for method, path in PROTECTED:
        response = getattr(client, method)(path, headers=headers)
        assert response.status_code == 401, path


def test_me_returns_the_profile_without_secrets(client, auth):
    response = client.get("/auth/me", headers=auth)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == SEED_EMAIL
    assert body["role"] == "admin"
    assert "password_hash" not in body
    assert "password" not in body


def test_email_update_persists_and_returns_a_usable_token(client, auth):
    response = client.patch(
        "/auth/me",
        headers=auth,
        json={"email": "New.Admin@DataCo.local", "current_password": SEED_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["email"] == "new.admin@dataco.local"

    fresh = {"Authorization": f"Bearer {body['access_token']}"}
    assert client.get("/auth/me", headers=fresh).json()["email"] == (
        "new.admin@dataco.local"
    )

    # The new address is the one that logs in from now on.
    assert client.post(
        "/auth/login",
        data={"username": "new.admin@dataco.local", "password": SEED_PASSWORD},
    ).status_code == 200
    assert client.post(
        "/auth/login",
        data={"username": SEED_EMAIL, "password": SEED_PASSWORD},
    ).status_code == 401


def test_email_update_requires_the_current_password(client, auth):
    response = client.patch(
        "/auth/me",
        headers=auth,
        json={"email": "new@dataco.local", "current_password": "wrong"},
    )

    assert response.status_code == 403
    assert client.get("/auth/me", headers=auth).json()["email"] == SEED_EMAIL


def test_email_update_rejects_an_invalid_address(client, auth):
    response = client.patch(
        "/auth/me",
        headers=auth,
        json={"email": "not-an-email", "current_password": SEED_PASSWORD},
    )

    assert response.status_code == 422


def test_email_update_rejects_the_current_address(client, auth):
    response = client.patch(
        "/auth/me",
        headers=auth,
        json={"email": SEED_EMAIL, "current_password": SEED_PASSWORD},
    )

    assert response.status_code == 422


def test_password_change_invalidates_previous_tokens(client, auth):
    response = client.post(
        "/auth/change-password",
        headers=auth,
        json={
            "current_password": SEED_PASSWORD,
            "new_password": NEW_PASSWORD,
        },
    )

    assert response.status_code == 200
    body = response.json()

    # The token used to make the call is now rejected...
    assert client.get("/auth/me", headers=auth).status_code == 401

    # ...and the one returned by the endpoint keeps the caller signed in.
    fresh = {"Authorization": f"Bearer {body['access_token']}"}
    assert client.get("/auth/me", headers=fresh).status_code == 200

    assert client.post(
        "/auth/login",
        data={"username": SEED_EMAIL, "password": NEW_PASSWORD},
    ).status_code == 200
    assert client.post(
        "/auth/login",
        data={"username": SEED_EMAIL, "password": SEED_PASSWORD},
    ).status_code == 401


def test_password_change_requires_the_current_password(client, auth):
    response = client.post(
        "/auth/change-password",
        headers=auth,
        json={"current_password": "wrong", "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 403
    assert client.post(
        "/auth/login",
        data={"username": SEED_EMAIL, "password": SEED_PASSWORD},
    ).status_code == 200


def test_password_change_enforces_the_policy(client, auth):
    for weak in ["short1", "nodigitsatall", "1234567890"]:
        response = client.post(
            "/auth/change-password",
            headers=auth,
            json={"current_password": SEED_PASSWORD, "new_password": weak},
        )
        assert response.status_code == 422, weak


def test_password_change_rejects_the_same_password(client, auth):
    response = client.post(
        "/auth/change-password",
        headers=auth,
        json={
            "current_password": SEED_PASSWORD,
            "new_password": SEED_PASSWORD,
        },
    )

    assert response.status_code == 422


def test_stored_account_never_contains_the_plaintext_password():
    from src.api import accounts

    raw = accounts.ACCOUNT_FILE.read_text(encoding="utf-8")

    assert SEED_PASSWORD not in raw
    assert "$argon2" in raw
