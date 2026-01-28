from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, UserResponse

router = APIRouter()
security = HTTPBearer()

from app.core.security import verify_firebase_token

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        # Use centralized security module for verification (handles initialization)
        decoded_token = verify_firebase_token(token)
        uid = decoded_token['uid']
        user = db.query(User).filter(User.firebase_uid == uid).first()
        if not user:
            # Auto-create user if valid firebase token but no DB record exists
            user = User(
                firebase_uid=uid, 
                email=decoded_token.get('email'),
                name=decoded_token.get('name') or decoded_token.get('email', '').split('@')[0]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user
