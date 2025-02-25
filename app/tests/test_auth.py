import jwt
import time
from fastapi import HTTPException
from app.auth.dependencies import get_current_user, get_current_admin_user, SECRET_KEY, OVERRIDE_KEY

def create_jwt_token(username, email, roles):
    payload = {
        "sub": username,
        "email": email,
        "role": roles,
        "exp": int(time.time()) + 3600, 
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def test_get_current_user():
    token = create_jwt_token("test_user", "test@example.com", ["user"])
    user = get_current_user(token=token)
    assert user["user_id"] == "test_user"
    assert user["email"] == "test@example.com"
    assert "user" in user["role"]


def test_get_current_admin_user():
    token = create_jwt_token("admin_user", "admin@example.com", ["admin"])
    user = get_current_user(token=token)
    admin_user = get_current_admin_user(user=user)
    assert admin_user["user_id"] == "admin_user"
    assert "admin" in admin_user["role"]


def test_invalid_token():
    invalid_token = "invalid.token.string"
    try:
        get_current_user(token=invalid_token)
        assert False, "Expected HTTPException for invalid token"
    except HTTPException as e:
        assert e.status_code == 401
        assert "Kunde inte validera dina uppgifter" in e.detail


def test_expired_token():
    expired_payload = {
        "sub": "expired_user",
        "email": "expired@example.com",
        "role": ["user"],
        "exp": int(time.time()) - 10, 
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")

    try:
        get_current_user(token=expired_token)
        assert False, "Expected HTTPException for expired token"
    except HTTPException as e:
        assert e.status_code == 401
        assert "Token har gått ut" in e.detail


def test_override_key():
    override_user = get_current_admin_user(user={}, override_key=OVERRIDE_KEY) 
    assert override_user["user_id"] == "override_admin"
    assert override_user["email"] == "admin@example.com"
    assert "admin" in override_user["role"]
