
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from ..models import User
from sqlalchemy import select
import datetime

# This doesn't actually validate the token, just extracts it from "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Verify the token with Google
        # This checks signature, expiration, and issuer
        id_info = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )

        email = id_info.get("email")
        if not email:
            raise credentials_exception
            
        # 2. Get or Create User in DB
        res = await db.execute(select(User).filter(User.email == email))
        user = res.scalars().first()
        
        if not user:
            name = id_info.get("name", email.split('@')[0])
            image = id_info.get("picture")
            
            user = User(
                email=email,
                name=name,
                image=image,
                created_at=datetime.datetime.now()
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        return user

    except ValueError:
        # Invalid token
        raise credentials_exception
    except Exception as e:
        print(f"Auth Error: {e}")
        raise credentials_exception
