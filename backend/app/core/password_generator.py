import secrets
import string


def generate_password(length: int = 16, use_upper: bool = True, use_lower: bool = True, use_digits: bool = True, use_symbols: bool = True) -> str:
    pools = []
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append('!@#$%^&*()-_=+[]{};:,.?/')

    if not pools:
        raise ValueError('Wybierz przynajmniej jeden zestaw znaków')

    alphabet = ''.join(pools)

    # gwarantuj min. 1 znak z każdej wybranej puli
    pwd = [secrets.choice(pool) for pool in pools]
    while len(pwd) < length:
        pwd.append(secrets.choice(alphabet))

    secrets.SystemRandom().shuffle(pwd)
    return ''.join(pwd)
