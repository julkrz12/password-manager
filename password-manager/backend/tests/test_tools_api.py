from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

# Ten test sprawdza endpoint:
# POST /tools/strength - czyli analizę siły hasła przez API.
# Te testy sprawdzają już pełną ścieżkę:
# HTTP request → FastAPI route → schema/Pydantic → core function → HTTP response
# Ten test ma potwierdzić, że API działa, zwraca poprawny format i da się go użyć z frontendu.
def test_strength_endpoint_returns_password_analysis():
    # 1. Wysyła żądanie do API z hasłem do analizy
    # To symuluje żądanie HTTP:
    # POST /tools/strength
    # Content-Type: application/json
    # z body:
    # {
    #     "password": "Password123!"
    # }
    response = client.post(
        "/tools/strength",
        json={"password": "Password123!"},
    )

    # 2. Sprawdza, czy endpoint odpowiedział poprawnie
    # Gdyby endpoint miał problem, moglibyśmy dostać np.:
    # - 422 Unprocessable Entity (np. jeśli schema Pydantic odrzuci dane)
    # - 500 Internal Server Error (np. jeśli funkcja core podniesie wyjątek)
    # - 404 - endpoint nie istnieje
    assert response.status_code == 200

    # 3. Odczytuje odpowiedź JSON
    # Czyli zamienia odpowiedź API na słownik Pythona.
    data = response.json()

    # 4. Sprawdza długość hasła
    assert data["length"] == len("Password123!")
    # 5. Sprawdza strukturę odpowiedzi
    # Czyli test nie wymusza dokładnej wartości entropii, ale wymusza, że API zwraca wszystkie najważniejsze pola:
    # entropy_bits        → oszacowana entropia hasła
    # charset_estimate    → oszacowany rozmiar alfabetu
    # score               → punktowa ocena hasła
    # label               → opisowa etykieta, np. słabe/średnie/silne
    # issues              → lista wykrytych problemów
    assert "entropy_bits" in data
    assert "charset_estimate" in data
    assert "score" in data
    assert "label" in data
    assert "issues" in data

    # 6. Sprawdza typy danych
    assert isinstance(data["entropy_bits"], (int, float)) # entropia powinna być liczbą
    assert isinstance(data["score"], int) # score powinien być int, np. 0-4
    assert isinstance(data["issues"], list) # issues powinno być listą, nawet jeśli jest pusta


def test_generate_endpoint_returns_password_with_requested_length():
    response = client.post(
        "/tools/generate",
        json={
            "length": 24,
            "use_upper": True,
            "use_lower": True,
            "use_digits": True,
            "use_symbols": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "password" in data
    assert isinstance(data["password"], str)
    assert len(data["password"]) == 24


def test_leak_endpoint_detects_password_from_offline_database():
    response = client.post(
        "/tools/leak",
        json={"password": "password"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "offline" in data
    assert data["offline"]["method"] == "offline"
    assert data["offline"]["pwned"] is True


def test_strength_endpoint_returns_422_when_password_missing():
    response = client.post(
        "/tools/strength",
        json={},
    )

    assert response.status_code == 422


def test_leak_endpoint_returns_422_when_password_missing():
    response = client.post(
        "/tools/leak",
        json={},
    )

    assert response.status_code == 422