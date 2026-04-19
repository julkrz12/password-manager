# Password Manager (MVP) — projekt zespołowy

Projekt realizuje temat: **Menedżer haseł z funkcją analizy siły haseł oraz wykrywaniem potencjalnych wycieków**.  
Zakres MVP: **lokalne szyfrowane przechowywanie haseł**, **analiza siły (entropy + heurystyki)**, **wykrywanie słabych/powtarzalnych haseł**, **wykrywanie potencjalnych wycieków (offline mock + opcjonalnie HIBP range/k‑anonymity)** oraz **generator silnych haseł**.

## 1) Stos technologiczny
- Backend: **Python + FastAPI**
- Baza: **SQLite** (plik `backend/data/vault.db`)
- Hash hasła głównego: **Argon2id**
- Szyfrowanie sekretów: **AES‑256‑GCM**
- Frontend: proste **HTML/CSS/JS** (serwowane z FastAPI)

> Uwaga: to projekt edukacyjny. Sesje są trzymane w pamięci procesu (`session_store.py`). Po restarcie backendu trzeba zalogować się ponownie.

## 2) Uruchomienie (lokalnie)

### Wymagania
- Python 3.10+ (rekomendowane 3.11)

### Kroki
```bash
# 1) Klonujesz repo
git clone <URL_DO_REPO>
cd password-manager

# 2) Tworzysz venv
python -m venv .venv
# Windows:
.\.venv\Scriptsctivate
# Linux/Mac:
source .venv/bin/activate

# 3) Instalujesz zależności
pip install -r backend/requirements.txt

# 4) Uruchamiasz API
uvicorn backend.app.main:app --reload

# 5) Otwierasz w przeglądarce
# http://127.0.0.1:8000/
```

### API Docs
- Swagger: http://127.0.0.1:8000/docs

## 3) Funkcje
- Rejestracja i logowanie z hasłem głównym (Argon2id)
- Dodawanie / listowanie / podgląd / edycja / usuwanie wpisów
- Szyfrowanie sekretów (login do serwisu + hasło + notatki) w bazie danych
- Analiza siły hasła (`/tools/strength`)
- Wykrywanie wycieków:
  - offline mock: `backend/data/breached_sha1.txt`
  - opcjonalnie HIBP k‑anonymity (range API) — patrz konfiguracja
- Wykrywanie duplikatów haseł w sejfie (`/vault/duplicates`) bez przechowywania haseł w czystej postaci
- Generator haseł (`/tools/generate`)

## 4) Konfiguracja (opcjonalna)
Utwórz plik `.env` w katalogu głównym:
```env
# SQLite w podkatalogu backend/data
DATABASE_URL=sqlite:///./data/vault.db

# TTL sesji (min)
SESSION_TTL_MINUTES=15

# HIBP Range API (k-anonymity)
ENABLE_HIBP_RANGE_API=false
HIBP_RANGE_BASE_URL=https://api.pwnedpasswords.com/range/
HIBP_USER_AGENT=PasswordManagerMVP (educational)
```

## 5) Testy
```bash
pytest -q
```

## 6) Struktura katalogów
```
password-manager/
  backend/
    app/
      core/
      routes/
      main.py
      db.py
      models.py
      schemas.py
    data/
      breached_sha1.txt
    requirements.txt
  frontend/
    index.html
    app.js
    styles.css
  .github/workflows/ci.yml
  README.md
```

## 7) Bezpieczeństwo — krótkie notatki
- Hasło główne jest **hashowane** (Argon2id) i nie jest przechowywane w postaci jawnej.
- Sekrety (hasła do serwisów) są **szyfrowane** AES‑GCM.
- Leak check w trybie HIBP używa **k‑anonymity** (wysyłany jest tylko prefix SHA‑1).
