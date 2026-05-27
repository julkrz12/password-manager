# Test funkcjonalny, bo sprawdza nie tylko pojedynczy mechanizm, ale wybór trybu pracy: offline albo HIBP.

import pytest

from app.core.leak_check import leak_check

# Ten test sprawdza trzy rzeczy: tryb tylko offline, tryb offline + HIBP oraz bezpieczne obsłużenie błędu HIBP.

@pytest.mark.asyncio
async def test_leak_check_returns_offline_result_when_hibp_disabled(monkeypatch):
    import app.core.leak_check as leak_check_module

    monkeypatch.setattr(
        leak_check_module.settings,
        "enable_hibp_range_api",
        False,
    )

    result = await leak_check("password")

    assert "offline" in result
    assert "online" not in result

    assert result["offline"]["method"] == "offline"
    assert result["offline"]["pwned"] is True


@pytest.mark.asyncio
async def test_leak_check_returns_offline_and_online_when_hibp_enabled(monkeypatch):
    import app.core.leak_check as leak_check_module

    async def fake_check_hibp_range(password: str):
        return {
            "method": "hibp_range",
            "pwned": True,
            "count": 12345,
        }

    monkeypatch.setattr(
        leak_check_module.settings,
        "enable_hibp_range_api",
        True,
    )
    monkeypatch.setattr(
        leak_check_module,
        "check_hibp_range",
        fake_check_hibp_range,
    )

    result = await leak_check("password")

    assert "offline" in result
    assert "online" in result

    assert result["offline"]["method"] == "offline"
    assert result["offline"]["pwned"] is True

    assert result["online"]["method"] == "hibp_range"
    assert result["online"]["pwned"] is True
    assert result["online"]["count"] == 12345


@pytest.mark.asyncio
async def test_leak_check_handles_hibp_error(monkeypatch):
    import app.core.leak_check as leak_check_module

    async def fake_check_hibp_range(password: str):
        raise RuntimeError("HIBP unavailable")

    monkeypatch.setattr(
        leak_check_module.settings,
        "enable_hibp_range_api",
        True,
    )
    monkeypatch.setattr(
        leak_check_module,
        "check_hibp_range",
        fake_check_hibp_range,
    )

    result = await leak_check("password")

    assert "offline" in result
    assert "online" in result

    assert result["online"]["method"] == "hibp_range"
    assert result["online"]["pwned"] is False
    assert "error" in result["online"]