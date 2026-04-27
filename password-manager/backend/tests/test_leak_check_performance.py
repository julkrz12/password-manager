# Cel: sprawdzić, czy przeszukiwanie większej bazy SHA-1 nie działa zbyt wolno.

# tests/test_leak_check_performance.py

import time

from app.core.leak_check import sha1_upper


def test_sha1_lookup_in_large_mock_database_is_fast():
    # Symulujemy dużą bazę hashy w pamięci
    leaked_hashes = {f"{i:040X}" for i in range(100_000)}

    leaked_password = "password"
    leaked_hashes.add(sha1_upper(leaked_password))

    start = time.perf_counter()

    result = sha1_upper(leaked_password) in leaked_hashes

    elapsed = time.perf_counter() - start

    assert result is True
    assert elapsed < 0.05

"""

Ten test nie sprawdza jeszcze pliku breached_sha1.txt, ale sprawdza kluczową ideę: lookup po hashach powinien być szybki, jeśli używamy set.

Jeżeli Twoja funkcja check_offline_sha1() za każdym razem czyta plik liniowo, to przy dużej bazie może być wolna. Wtedy warto później zrobić cache.

"""