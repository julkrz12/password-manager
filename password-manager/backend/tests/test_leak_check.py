from app.core.leak_check import check_offline_sha1, sha1_hex, sha1_upper

# Testy test_leak_check.py

# Tu sprawdziłbym dwa przypadki:

# - hasło jest w bazie wycieków
# - hasła nie ma w bazie wycieków

# W pliku data/breached_sha1.txt jest hash hasła:
#
# password

def test_sha1_hex_returns_uppercase_hash():
    result = sha1_hex("password")

    assert result == "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8"

def test_sha1_upper_for_password():
    assert sha1_upper("password") == "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8"


def test_password_is_found_in_offline_breach_database():
    result = check_offline_sha1("password")

    assert result["method"] == "offline"
    assert result["pwned"] is True


def test_password_is_not_found_in_offline_breach_database():
    result = check_offline_sha1("VeryStrongPassword_NotInMockDb_123!")

    assert result["method"] == "offline"
    assert result["pwned"] is False