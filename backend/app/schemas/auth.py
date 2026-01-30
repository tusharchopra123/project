
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Login Payload (from Google Frontend)
class GoogleLoginRequest(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_token: str  # Verify this if doing backend verification, else just trust for now (dev)

# Token Response
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
