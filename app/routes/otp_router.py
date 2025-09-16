# from http.client import HTTPException
# import random

# from fastapi import APIRouter, logger
# from pydantic import BaseModel, EmailStr

# from app.utils.email_sender import send_admin_credentials_email
# from app.utils.otp_sender import generate_otp, store_otp, verify_otp
# from app.utils.security import hash_password
# class ForgotPasswordRequest(BaseModel):
#     email: EmailStr
#     full_name: str = "User"   # Optional, fallback to 'User'

# class VerifyOTPRequest(BaseModel):
#     email: EmailStr
#     otp: str

# class ResetPasswordRequest(BaseModel):
#     email: EmailStr
#     otp: str
#     new_password: str

# otp_router= APIRouter(prefix="/api", tags=["OTP Management"])
# @otp_router.post("/forgot-password/send-otp")
# async def send_otp(req: ForgotPasswordRequest):
#     try:
#         otp = generate_otp()
#         print(otp)
#         store_otp(req.email, otp)

#         # Send OTP email
#         await send_admin_credentials_email(full_name=req.full_name, email=req.email, otp=otp,tenant_name="RishiKrishi", role="User", is_otp=True    )

#         return {"message": "OTP sent successfully to email"}
#     except Exception as e:
#         # logger.error(f"OTP request failed: {str(e)}")
#         raise HTTPException(status_code=400, detail="Failed to send OTP")

# @otp_router.post("/forgot-password/verify-otp")
# async def verify_otp_endpoint(req: VerifyOTPRequest):
#     if verify_otp(req.email, req.otp):
#         return {"message": "OTP verified successfully"}
#     else:
#         raise HTTPException(status_code=401, detail="Invalid or expired OTP")

# @otp_router.post("/forgot-password/reset")
# async def reset_password(req: ResetPasswordRequest):
#     if verify_otp(req.email, req.otp):
#         hashed = hash_password(req.new_password)
#         # TODO: Update your DB with `hashed`
#         logger.debug(f"Password for {req.email} reset to hashed value {hashed}")
#         return {"message": "Password reset successfully"}
#     else:
#         raise HTTPException(status_code=401, detail="Invalid or expired OTP")


import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.models.users_model import update_user_password_in_db
from app.services.superadmin_service import get_tenant_by_id_service
from app.utils import security
from app.utils.email_sender import send_admin_credentials_email
from app.utils.otp_sender import generate_otp, store_otp, verify_otp
from app.utils.security import hash_password

logger = logging.getLogger(__name__)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    tenant_id: str
    full_name: Optional[str] = "User"   # Optional, fallback to 'User'

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    tenant_id: str
    new_password: str

otp_router = APIRouter(prefix="/api", tags=["OTP Management"])

@otp_router.post("/forgot-password/send-otp")
async def send_otp(req: ForgotPasswordRequest):
    try:
        otp = generate_otp()
        logger.debug(f"Generated OTP {otp} for {req.email}")
        store_otp(req.email, otp)
        tenant_name=get_tenant_by_id_service(req.tenant_id)[1]
        await send_admin_credentials_email(
            full_name=req.full_name,
            email=req.email,
            tenant_name=tenant_name,
            role="User",
            is_otp=True,
            otp=otp,
        )
        return {"message": "OTP sent successfully to email"}
    except Exception as e:
        logger.error(f"OTP request failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to send OTP")

@otp_router.post("/forgot-password/verify-otp")
async def verify_otp_endpoint(req: VerifyOTPRequest):
    if verify_otp(req.email, req.otp):
        return {"message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

@otp_router.post("/forgot-password/reset")
async def reset_password(req: ResetPasswordRequest):
    if verify_otp(req.email, req.otp):
        print("otp verified")
        hashed_password = security.hash_password(req.new_password)
        logger.debug(f"Password for {req.email} reset to hashed value {hashed_password}")
        # TODO: update DB with `hashed`
        update_user_password_in_db(req.email,hashed_password,req.tenant_id)  # Implement this function as needed  

        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
