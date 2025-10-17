from fastapi import HTTPException
from passlib.context import CryptContext
from app.models.admin_model import get_admin_email, get_admins_login, get_admins_login_by_email, get_admins_login_by_tenant, update_admin_password
from app.models.tenant_model import get_admin_by_email_and_tenant
from app.utils.security import create_access_token,create_refresh_token, hash_password, verify_password



    
    
def login_admin_step_one(user_name: str, password: str) -> dict:
    if not user_name:
        raise HTTPException(status_code=400, detail="Email or phone number is required")

    email = user_name if "@" in user_name else None
    phone = user_name if "@" not in user_name else None
    
    admins = get_admins_login(email=email, phone=phone)
    if not admins:
        if email:
            raise HTTPException(status_code=401, detail="No admin account with this email")
        else:
            raise HTTPException(status_code=401, detail="No admin account with this phone number")

    valid_tenants = []
    for admin in admins:
        if verify_password(password, admin["password"]):
            valid_tenants.append({
                "tenant_id": admin["tenant_id"],
                "tenant_name": admin["tenant_name"],
            })

    if not valid_tenants:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"tenants": valid_tenants}


def login_admin_step_two(tenant_id: str, user_name: str, password: str = None) -> dict:
    email = user_name if "@" in user_name else None
    phone = user_name if "@" not in user_name else None

    admins = get_admins_login_by_tenant(tenant_id, email=email, phone=phone)
    if not admins:
        if email:
            raise HTTPException(status_code=404, detail="User not found with this email for the tenant")
        else:
            raise HTTPException(status_code=404, detail="User not found with this phone number for the tenant")

    matched_admin = None
    for admin in admins:
        if password is None or verify_password(password, admin["password"]):
            matched_admin = admin
            break

    if not matched_admin:
        raise HTTPException(status_code=401, detail="Invalid Password")

    if not matched_admin["is_active"]:
        raise HTTPException(status_code=403, detail="Account is inactive")

    access_data = {
        "sub": matched_admin["user_id"],
        "role": matched_admin["role"],
        "tenant_id": matched_admin["tenant_id"],
        "full_name": matched_admin["full_name"],
        "email": matched_admin["email"],
        "schema_id": matched_admin["schema_id"],
    }
    access_token = create_access_token(access_data)
    refresh_token = create_refresh_token(access_data)

    return {
        "full_name": matched_admin["full_name"],
        "tenant_name": matched_admin["tenant_name"],
        "phone": matched_admin["phone_no"],
        "role": matched_admin["role"],
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": matched_admin["user_id"]
    }
 

def change_admin_password_service(tenant_id: str, email: str, old_password: str, new_password: str) -> str:
    admin = get_admin_by_email_and_tenant(email, tenant_id)

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found for this tenant")

    if not verify_password(old_password, admin["password"]):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    
    if old_password == new_password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as old password")

    new_hashed_password = hash_password(new_password)
    updated = update_admin_password(admin["id"], new_hashed_password)

    if not updated:
        raise HTTPException(status_code=500, detail="Password update failed")

    return "Password updated successfully"

