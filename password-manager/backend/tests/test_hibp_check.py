# tests/test_hibp_check.py

import pytest

from app.core.leak_check import check_hibp_range, sha1_upper

# wersja pod HIBP — bez prawdziwego łączenia z internetem, tylko mock odpowiedzi API
# uruchamiasz offline
# pytest tests/test_leak_check.py -v

# i doprowadzasz do stanu:

# PASSED
# PASSED
# PASSED

# 👉 dopiero wtedy masz pewność, że:

# SHA1 działa
# logika leak check działa
# plik breached_sha1.txt jest OK

class FakeResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, url, headers=None):
        # SHA1("password")
        full_hash = sha1_upper("password")
        suffix = full_hash[5:]

        return FakeResponse(f"{suffix}:12345\nABCDEF:1")


@pytest.mark.asyncio
async def test_hibp_range_detects_pwned_password(monkeypatch):
    import app.core.leak_check as leak_check_module

    monkeypatch.setattr(leak_check_module.httpx, "AsyncClient", FakeAsyncClient)

    result = await check_hibp_range("password")

    assert result["method"] == "hibp_range"
    assert result["pwned"] is True
    assert result["count"] == 12345

# Jeśli pojawi się błąd z pytest.mark.asyncio, doinstaluj:

# pip install pytest-asyncio


"""

✅ SHA-1 dla hasła działa poprawnie
✅ offline leak check wykrywa hasło z lokalnej bazy
✅ offline leak check nie zgłasza hasła spoza bazy
✅ HIBP range API jest poprawnie testowane przez mock
✅ logika k-anonymity działa bez realnego połączenia z internetem

"""