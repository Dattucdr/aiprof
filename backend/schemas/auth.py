from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    hospital_name: str
    hospital_code: str
    timezone: str = "Asia/Kolkata"

    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    hospital_id: int | None
    is_active: bool

    class Config:
        from_attributes = True