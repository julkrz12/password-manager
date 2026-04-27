import hashlib
import pathlib
import httpx
from .config import settings

BREACH_FILE = pathlib.Path(__file__).resolve().parents[2] / "data" / "breached_sha1.txt"


def sha1_upper(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest().upper()


def check_offline_sha1(password: str) -> dict:
    """
    Offline / mock check – porównanie pełnego SHA1 z lokalnym plikiem.
    """
    h = sha1_upper(password)

    if not BREACH_FILE.exists():
        return {
            "method": "offline",
            "pwned": False,
            "note": "Brak breached_sha1.txt – pominięto offline check",
        }

    with BREACH_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip().upper() == h:
                return {"method": "offline", "pwned": True}

    return {"method": "offline", "pwned": False}


async def check_hibp_range(password: str) -> dict:
    """
    Have I Been Pwned – k-anonymity (wysyłamy tylko 5 znaków SHA1).
    Co robi: hasło → SHA-1 → prefix 5 znaków → request do HIBP → lokalne porównanie suffixu
    Przykład dla hasła password:
    SHA1(password) = 5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
    prefix = 5BAA6
    suffix = 1E4C9B93F3F0682250B6CF8331B7EE68FD8
    Do HIBP idzie tylko:
    https://api.pwnedpasswords.com/range/5BAA6
    """
    sha1 = sha1_upper(password)
    prefix, suffix = sha1[:5], sha1[5:]

    url = settings.hibp_range_base_url + prefix
    headers = {"User-Agent": settings.hibp_user_agent}

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

        for line in response.text.splitlines():
            parts = line.split(":")
            if len(parts) >= 2 and parts[0].upper() == suffix:
                return {
                    "method": "hibp_range",
                    "pwned": True,
                    "count": int(parts[1]),
                }

    return {"method": "hibp_range", "pwned": False}


# async def leak_check(password: str) -> dict:
#     """
#     Wrapper – offline zawsze, online opcjonalnie.
#     """
#     offline = check_offline_sha1(password)

#     if settings.enable_hibp_range_api:
#         try:
#             online = await check_hibp_range(password)
#         except Exception as e:
#             online = {
#                 "method": "hibp_range",
#                 "pwned": False,
#                 "error": str(e),
#             }
#         return {"offline": offline, "online": online}

#     return {"offline": offline}


async def leak_check(password: str, use_hibp: bool = False) -> dict:
    """
    Wrapper – offline zawsze, online opcjonalnie.
    HIBP działa tylko gdy:
    1. globalnie jest włączony w settings
    2. użytkownik zaznaczył use_hibp
    """

    print("DEBUG use_hibp =", use_hibp)
    print("DEBUG enable_hibp_range_api =", settings.enable_hibp_range_api)


    offline = check_offline_sha1(password)

    if settings.enable_hibp_range_api and use_hibp:
        try:
            online = await check_hibp_range(password)
        except Exception as e:
            online = {
                "method": "hibp_range",
                "pwned": False,
                "error": str(e),
            }
        return {
            "offline": offline, 
            "online": online
        }

    return {
        "offline": offline
    }