from backend.app.core.password_strength import analyze_password


def test_strength_short():
    r = analyze_password('abc')
    assert r['score'] < 30


def test_strength_strongish():
    r = analyze_password('S3cur3!Passphrase-2026-OK')
    assert r['score'] >= 40
