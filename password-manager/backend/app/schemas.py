from pydantic import BaseModel, Field
from typing import Optional


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    master_password: str = Field(min_length=8, max_length=256)


class LoginRequest(BaseModel):
    username: str
    master_password: str


class SessionResponse(BaseModel):
    token: str
    ttl_minutes: int


class EntryCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    url: str = Field(default='', max_length=512)
    account_username: str = Field(default='', max_length=256)
    password: str = Field(min_length=1, max_length=512)
    notes: str = Field(default='', max_length=4096)


class EntryUpdateRequest(BaseModel):
    url: Optional[str] = Field(default=None, max_length=512)
    account_username: Optional[str] = Field(default=None, max_length=256)
    password: Optional[str] = Field(default=None, max_length=512)
    notes: Optional[str] = Field(default=None, max_length=4096)


class EntryListItem(BaseModel):
    id: int
    title: str
    url: str


class EntryDetail(BaseModel):
    id: int
    title: str
    url: str
    account_username: str
    password: str
    notes: str


class StrengthResponse(BaseModel):
    length: int
    charset_estimate: int
    entropy_bits: float
    score: int
    label: str
    issues: list[str]


class LeakCheckRequest(BaseModel):
    password: str


class LeakCheckResponse(BaseModel):
    offline: dict
    online: Optional[dict] = None


class GeneratePasswordRequest(BaseModel):
    length: int = 16
    use_upper: bool = True
    use_lower: bool = True
    use_digits: bool = True
    use_symbols: bool = True


class GeneratePasswordResponse(BaseModel):
    password: str
