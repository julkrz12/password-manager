from fastapi import APIRouter
from ..schemas import StrengthResponse, LeakCheckRequest, LeakCheckResponse, GeneratePasswordRequest, GeneratePasswordResponse
from ..core.password_strength import analyze_password
from ..core.leak_check import leak_check
from ..core.password_generator import generate_password

router = APIRouter(prefix='/tools', tags=['tools'])


@router.post('/strength', response_model=StrengthResponse)
def strength(req: LeakCheckRequest):
    return analyze_password(req.password)


@router.post('/leak', response_model=LeakCheckResponse)
async def leak(req: LeakCheckRequest):
    res = await leak_check(req.password)
    return res


@router.post('/generate', response_model=GeneratePasswordResponse)
def gen(req: GeneratePasswordRequest):
    return {'password': generate_password(req.length, req.use_upper, req.use_lower, req.use_digits, req.use_symbols)}
