# Test SHA-1 dla nietypowych znaków


# tests/test_sha1_inputs.py

from app.core.leak_check import sha1_upper


def test_sha1_upper_handles_unicode():
    result = sha1_upper("ąęśćźżółń") # hasło z polskimi znakami

    assert isinstance(result, str) # sprawdzamy, że to string
    assert len(result) == 40 # sprawdzamy długość hash (40 znaków dla SHA-1)
    assert result == result.upper() # sprawdzamy, że hash jest uppercase


def test_sha1_upper_handles_empty_password():
    result = sha1_upper("") # hasło puste

    assert isinstance(result, str) # sprawdzamy, że to string
    assert len(result) == 40 # sprawdzamy długość hash (40 znaków dla SHA-1)
    assert result == result.upper() # sprawdzamy, że hash jest uppercase    