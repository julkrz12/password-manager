from fastapi import APIRouter
from ..schemas import StrengthResponse, LeakCheckRequest, LeakCheckResponse, GeneratePasswordRequest, GeneratePasswordResponse
from ..core.password_strength import analyze_password
from ..core.leak_check import leak_check
from ..core.password_generator import generate_password

#from ..core.config import settings
#from app.core.leak_check import leak_check

router = APIRouter(prefix='/tools', tags=['tools'])


@router.post('/strength', response_model=StrengthResponse)
def strength(req: LeakCheckRequest):
    return analyze_password(req.password)


# @router.post('/leak', response_model=LeakCheckResponse)
# async def leak(req: LeakCheckRequest):
#     res = await leak_check(req.password)
#     return res

#@router.post("/leak", response_model=LeakCheckResponse)
@router.post(
    "/leak",
    response_model=LeakCheckResponse,
    response_model_exclude_none=True,
)
async def leak(req: LeakCheckRequest):
    return await leak_check(
        req.password,
        use_hibp=req.use_hibp,
    )


@router.post('/generate', response_model=GeneratePasswordResponse)
def gen(req: GeneratePasswordRequest):
    return {'password': generate_password(req.length, req.use_upper, req.use_lower, req.use_digits, req.use_symbols)}

# @router.post("/leak")
# async def leak_check_endpoint(payload: LeakCheckRequest):
#     result = {}

#     # zawsze offline
#     result["offline"] = check_offline_sha1(payload.password)

#     # tylko jeśli spełnione oba warunki
#     if settings.enable_hibp_range_api and payload.use_hibp:
#         try:
#             result["online"] = await check_hibp_range(payload.password)
#         except Exception as e:
#             result["online"] = {
#                 "method": "hibp_range",
#                 "pwned": False,
#                 "error": str(e)
#             }

#     return result

# @router.post("/leak")
# async def check_leak(payload: LeakCheckRequest):
#     return await leak_check(
#         payload.password,
#         use_hibp=payload.use_hibp,
#     )