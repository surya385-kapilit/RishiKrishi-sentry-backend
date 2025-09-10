from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        # Prevent using refresh token for normal API calls
        if payload.get("type") == "refresh":
            raise HTTPException(status_code=403, detail="Refresh token cannot be used to access resources")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Prevent using refresh token for admin endpoints
        if payload.get("type") == "refresh":
            raise HTTPException(status_code=401, detail="Refresh token cannot be used as admin token")

        tenant_id = payload.get("tenant_id")
        role = payload.get("role")
        user_id = payload.get("user_id")
        email = payload.get("email")

        if not tenant_id:
            raise HTTPException(status_code=400, detail="Missing tenant_id in token")

        return {
            "tenant_id": tenant_id,
            "role": role,
            "user_id": user_id,
            "email": email
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    

def create_reset_token(user_id: str, email: str, expires_minutes: int = 15):
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": user_id,
        "email": email,
        "action": "forgot_password",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

