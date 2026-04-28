from app.core.password_generator import generate_password


def test_generate_password_default_length():
    password = generate_password()

    assert isinstance(password, str)
    assert len(password) >= 12


def test_generate_password_custom_length():
    password = generate_password(length=20)

    assert len(password) == 20


def test_generate_password_contains_expected_character_types():
    password = generate_password(length=64)

    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(not c.isalnum() for c in password)

# uruchomienie testów

# Przejdź do katalogu backendu
# ▶️ 5. Uruchom konkretny test

# pytest tests/test_password_generator.py

# ▶️ 6. Uruchom konkretną funkcję testową

# pytest tests/test_password_generator.py::test_generate_password_default_length

# 🚀 Najprostszy start (TL;DR)

# cd backend
# source venv/bin/activate
# pip install -r requirements.txt
# pytest -v