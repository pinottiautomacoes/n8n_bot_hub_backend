import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status
from app.core.config import settings
import os
import json

if not firebase_admin._apps:
    firebase_cred = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    
    try:
        if firebase_cred and os.path.exists(firebase_cred):
             # It's a file path
            cred = credentials.Certificate(firebase_cred)
        else:
            # Assume it's a JSON string
            service_account_info = json.loads(firebase_cred)
            cred = credentials.Certificate(service_account_info)
            
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized via security module")
    except Exception as e:
        print(f"Warning: Firebase Admin initialization failed in security module: {e}")


async def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token.
    
    Args:
        token: Firebase ID token from Authorization header
        
    Returns:
        Decoded token containing user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
