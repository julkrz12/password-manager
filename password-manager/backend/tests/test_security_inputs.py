# Test odporności na nietypowe hasła

# tests/test_security_inputs.py

import pytest

from app.core.leak_check import sha1_upper, check_offline_sha1
from app.core.password_strength import analyze_password


@pytest.mark.parametrize("password", [
    "",
    " ",
    "     ",
    "a",
    "ąęśćźżółń",
    "🔥🔐🚀",
    "a" * 1000,
    "password\nadmin",
    "password\tadmin",
])
def test_leak_check_accepts_unusual_password_inputs(password):
    result = check_offline_sha1(password)

    assert isinstance(result, dict)
    assert "method" in result
    assert "pwned" in result
    assert result["method"] == "offline"
    assert isinstance(result["pwned"], bool)


@pytest.mark.parametrize("password", [
    "",
    " ",
    "a",
    "password",
    "Password123!",
    "ąęśćźżółń123!",
    "🔥🔐🚀Password123!",
    "a" * 1000,
])
def test_password_strength_accepts_unusual_password_inputs(password):
    result = analyze_password(password)

    assert isinstance(result, dict)
    assert "entropy_bits" in result
    assert "score" in result