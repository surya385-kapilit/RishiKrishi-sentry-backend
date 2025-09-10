from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
from app.utils.security import SECRET_KEY, ALGORITHM, create_access_token

router = APIRouter()

# Pydantic model to accept refresh token in the body
class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh-token")
def refresh_token(data: RefreshTokenRequest):
    refresh_token = data.refresh_token  # get token from request body

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        # user_id = payload.get("sub")
        access_token_data ={
            "sub": payload.get("sub"),
            "role": payload.get("role"),
            "tenant_id": payload.get("tenant_id"),
            "schema_id": payload.get("schema_id"),
            "full_name": payload.get("full_name"),
            "email": payload.get("email")
            
            
        }
        new_access_token = create_access_token(access_token_data)

        return {"access_token": new_access_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
