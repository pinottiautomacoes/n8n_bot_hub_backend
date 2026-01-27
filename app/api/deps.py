from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_firebase_token
from app.models.user import User as UserModel
from app.schemas.user import UserCreate


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependency to get the current authenticated user.
    
    1. Verifies Firebase token from Authorization header
    2. Fetches or creates user in PostgreSQL
    3. Returns user object
    """

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Verify Firebase token
    decoded_token = await verify_firebase_token(authorization)
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    name = decoded_token.get("name")
    
    # print(f"good! {firebase_uid}, {email}, {name}")

    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing uid"
        )
    
    # Check if user exists in database
    user = db.query(UserModel).filter(UserModel.firebase_uid == firebase_uid).first()

    # Create user if doesn't exist
    if not user:
        user = UserModel(
            firebase_uid=firebase_uid,
            email=email,
            name=name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """
    Dependency to get current active user.
    Can be extended with additional checks (e.g., is_active flag).
    """
    return current_user
