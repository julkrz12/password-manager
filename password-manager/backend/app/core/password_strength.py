import math
import re
from dataclasses import dataclass

COMMON_WORDS = {
    'password','haslo','qwerty','admin','welcome','letmein','iloveyou','monkey','dragon',
    '123456','1234567','12345678','123456789','1234567890'
}

KEYBOARD_SEQS = [
    'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
    '1234567890'
]


def _charset_size(pw: str) -> int:
    size = 0
    if re.search(r'[a-z]', pw):
        size += 26
    if re.search(r'[A-Z]', pw):
        size += 26
    if re.search(r'[0-9]', pw):
        size += 10
    if re.search(r'[^a-zA-Z0-9]', pw):
        # przybliżenie liczby znaków specjalnych
        size += 32
    return max(size, 1)


def _has_sequences(pw: str) -> bool:
    low = pw.lower()
    for seq in KEYBOARD_SEQS:
        if seq in low or seq[::-1] in low:
            return True
    # prosta sekwencja liter/ cyfr rosnąca
    for i in range(len(low) - 2):
        a, b, c = low[i], low[i+1], low[i+2]
        if a.isalpha() and b.isalpha() and c.isalpha():
            if ord(b) == ord(a) + 1 and ord(c) == ord(b) + 1:
                return True
        if a.isdigit() and b.isdigit() and c.isdigit():
            if int(b) == int(a) + 1 and int(c) == int(b) + 1:
                return True
    return False


def _repeats(pw: str) -> bool:
    return bool(re.search(r'(.)', pw))  # np. aaa


def _looks_like_date(pw: str) -> bool:
    # 2026-04-19, 19/04/2026, 19042026 itp.
    return bool(re.search(r'(19|20)\d{2}[-/.]?\d{2}[-/.]?\d{2}', pw)) or bool(re.search(r'\d{2}[-/.]\d{2}[-/.](19|20)\d{2}', pw))


def analyze_password(pw: str) -> dict:
    issues = []

    length = len(pw)
    charset = _charset_size(pw)
    entropy = math.log2(charset) * length

    # heurystyki kar
    if length < 8:
        issues.append('Za krótkie (min. 8 znaków)')
        entropy *= 0.55
    elif length < 12:
        issues.append('Warto zwiększyć długość do 12+ znaków')
        entropy *= 0.85

    if pw.lower() in COMMON_WORDS:
        issues.append('Bardzo popularne / słownikowe hasło')
        entropy *= 0.25

    if _has_sequences(pw):
        issues.append('Wykryto sekwencję (np. qwerty/1234/abcd)')
        entropy *= 0.65

    if _repeats(pw):
        issues.append('Wykryto powtarzające się znaki (np. aaa)')
        entropy *= 0.75

    if _looks_like_date(pw):
        issues.append('Wygląda jak data — łatwe do odgadnięcia')
        entropy *= 0.8

    # score 0-100 na bazie entropii
    # ~ 28b: słabe, 36b: średnie, 60b+: mocne
    score = int(max(0, min(100, (entropy / 60) * 100)))

    if score < 25:
        label = 'Bardzo słabe'
    elif score < 50:
        label = 'Słabe'
    elif score < 70:
        label = 'Średnie'
    elif score < 85:
        label = 'Dobre'
    else:
        label = 'Bardzo dobre'

    return {
        'length': length,
        'charset_estimate': charset,
        'entropy_bits': round(entropy, 2),
        'score': score,
        'label': label,
        'issues': issues,
    }
