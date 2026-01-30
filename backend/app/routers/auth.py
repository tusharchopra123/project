
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..core.database import get_db
from ..models import User
import datetime
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

class UserLogin(BaseModel):
    name: str
    email: str
    image: str | None = None

@router.post("/login")
async def login_user(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Syncs the Google User with our backend database.
    Creates user if not exists.
    """
    result = await db.execute(select(User).filter(User.email == user_data.email))
    user = result.scalars().first()

    if not user:
        user = User(
            name=user_data.name,
            email=user_data.email,
            picture=user_data.image,
            created_at=datetime.datetime.now()
        )
        db.add(user)
    else:
        # Update details if changed
        user.name = user_data.name
        user.picture = user_data.image
    
    await db.commit()
    await db.refresh(user)
    
    return {"status": "success", "user_id": user.id}
