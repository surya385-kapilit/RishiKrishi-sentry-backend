# services/supervisor_service.py
from fastapi import HTTPException
from app.models.admin_model import get_admins_login_by_email
from app.utils.security import verify_password, create_access_token, create_refresh_token

def login_supervisor_service(email: str, password: str) -> dict:
    supervisors = get_admins_login_by_email(email)  

    if not supervisors:
        raise HTTPException(status_code=401, detail="No supervisor accounts with this email")

    matched_supervisor = None
    for sup in supervisors:
        if sup["role"].upper() == "SUPERVISOR" and verify_password(password, sup["password"]):
            matched_supervisor = sup
            break  

    if not matched_supervisor:
        raise HTTPException(status_code=401, detail="Invalid Email or Password")

    if not matched_supervisor["is_active"]:
        raise HTTPException(status_code=403, detail="Account is inactive")

    access_data = {
        "sub": matched_supervisor["user_id"],
        "role": matched_supervisor["role"],
        "tenant_id": matched_supervisor["tenant_id"],
        # "email": matched_supervisor["email"],
        "schema_id": matched_supervisor["schema_id"]
    }
    access_token = create_access_token(access_data)
    refresh_token = create_refresh_token(access_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "full_name": matched_supervisor["full_name"],
        "tenant_name": matched_supervisor["tenant_name"],
        # "email": matched_supervisor["email"],
        # "is_active": matched_supervisor["is_active"],
        
    }
