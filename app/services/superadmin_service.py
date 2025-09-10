from app.models.superadmin_model import (
    get_superadmin_by_email, create_superadmin, get_all_superadmins,
    get_superadmin_by_id, update_superadmin_fullname,
    delete_superadmin
)
from app.models.tenant_model import (
    create_tenant, get_admin_by_email_and_tenant, get_tenant_by_id, get_all_tenants, update_tenant,
    delete_tenant, get_tenant_by_domain
)
from app.models.admin_model import (
    generate_alphanumeric_id, generate_random_password, get_admin_by_id, get_admin_email, get_all_admins, get_admins_by_tenant, create_admin,
    update_admin_password,
    update_admin, delete_admin
)
from app.utils.security import verify_password, create_access_token, hash_password, create_refresh_token
from app.utils.email_sender import send_admin_credentials_email
from app.config.db import db_pool
from fastapi import HTTPException

import os
from dotenv import load_dotenv

load_dotenv()

import httpx
# Superadmin Services
def login_superadmin_service(email, password):
    user = get_superadmin_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Email not found")
    
    stored_email, stored_password, role ,full_name= user
    
    if not verify_password(password, stored_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    token_payload = {
        "sub": stored_email,
        "role": role
    }
    
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)
    
    return access_token, refresh_token, role, full_name

def create_superadmin_service(email, password, role="SUPERADMIN",full_name=None):
    existing_user = get_superadmin_by_email(email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = hash_password(password)
    return create_superadmin(email, hashed_password, role, full_name)

def get_all_superadmins_service():
    return get_all_superadmins()

def get_superadmin_by_id_service(superadmin_id):
    superadmin = get_superadmin_by_id(superadmin_id)
    if not superadmin:
        raise HTTPException(status_code=404, detail="Superadmin not found")
    return superadmin

# def update_superadmin_service(superadmin_id, email=None, role=None, full_name=None):
#     superadmin = get_superadmin_by_id(superadmin_id)
#     if not superadmin:
#         raise HTTPException(status_code=404, detail="Superadmin not found")

#     if email:
#         existing_user = get_superadmin_by_email(email)
#         if existing_user and existing_user[0] != superadmin[1]:
#             raise HTTPException(status_code=400, detail="Email already exists")
#         update_superadmin_email(superadmin_id, email)

#     if role:
#         update_superadmin_role(superadmin_id, role)

#     if full_name:
#         update_superadmin_fullname(superadmin_id, full_name)

#     return get_superadmin_by_id(superadmin_id)

# def update_superadmin_password_service(email, current_password, new_password):
#     user = get_superadmin_by_email(email)
#     if not user:
#         raise HTTPException(status_code=404, detail="Superadmin not found")
    
#     stored_email, stored_password, role = user
    
#     if not verify_password(current_password, stored_password):
#         raise HTTPException(status_code=401, detail="Current password is incorrect")
    
#     hashed_password = hash_password(new_password)
#     update_superadmin_password(email, hashed_password)
#     return True


def update_superadmin_service(superadmin_id, full_name):
    superadmin = get_superadmin_by_id(superadmin_id)
    if not superadmin:
        raise HTTPException(status_code=404, detail="Superadmin not found")

    success = update_superadmin_fullname(superadmin_id, full_name)
    if not success:
        raise HTTPException(status_code=400, detail="No changes made")

    return get_superadmin_by_id(superadmin_id)


def delete_superadmin_service(superadmin_id):
    superadmin = get_superadmin_by_id(superadmin_id)
    if not superadmin:
        raise HTTPException(status_code=404, detail="Superadmin not found")
    
    return delete_superadmin(superadmin_id)


SLAVE_API_URL = os.getenv("SLAVE_API_URL")

def create_tenant_service(tenant_name, tenant_domain,auth_header): 
    existing_tenant = get_tenant_by_domain(tenant_name,tenant_domain)
    print("Existing tenant ", existing_tenant)
    
    for tenant in existing_tenant:
        if tenant[0] == tenant_name:
            raise HTTPException(status_code=400, detail="Tenant name already exists")
        if tenant[1] == tenant_domain:
            raise HTTPException(status_code=400, detail="Tenant domain already exists")


    # Call Slave API with schema_name
    try:
        print(SLAVE_API_URL)
        response = httpx.post(f"{SLAVE_API_URL}/api/external/create-tenant", json={"schema_name": tenant_name},
                              headers={"Authorization": auth_header},
                              timeout=httpx.Timeout(10.0, read=60.0))
        response.raise_for_status()
        schema_data = response.json()
        schema_id = schema_data.get("schema_name")

        if not schema_id:
            raise HTTPException(status_code=500, detail="Failed to retrieve schema_name from Slave service")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Slave service: {str(e)}")

    # Pass the real schema_id to DB insert
    return create_tenant(tenant_name, tenant_domain, schema_id)


def get_all_tenants_service():
    return get_all_tenants()

def get_tenant_by_id_service(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

def update_tenant_service(tenant_id, is_active):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    print("is_activate",is_active)
    success = update_tenant(tenant_id, is_active=is_active)
    if not success:
        raise HTTPException(status_code=400, detail="No changes made")

    return get_tenant_by_id(tenant_id) 

def delete_tenant_service(tenant_id):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return delete_tenant(tenant_id)


#Admin Services
async def create_tenant_admin_service(
    tenant_id, full_name, email, role="ADMIN", phone_no=None, user_id=None, hashed_password=None
):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant_name = tenant[1]  # Assuming second column is tenant_name

    existing_admin_in_tenant = get_admin_by_email_and_tenant(email, tenant_id)
    if existing_admin_in_tenant:
        raise HTTPException(status_code=400, detail="User already exists in this tenant")

    if not user_id:
        existing_admin = get_admin_email(email)
        user_id = existing_admin["user_id"] if existing_admin else generate_alphanumeric_id()

    # If password not provided, generate + send email
    if not hashed_password:
        plain_password = generate_random_password()
        print("Generated Password: ", plain_password)
        hashed_password = hash_password(plain_password)

        email_sent = await send_admin_credentials_email(full_name, email, plain_password, tenant_name, role)
        
        if not email_sent:
            raise HTTPException(status_code=500, detail="Email sending failed, user not created")
    
    admin_id = create_admin(
        tenant_id=tenant_id,
        full_name=full_name,
        email=email,
        hashed_password=hashed_password,
        role=role,
        user_id=user_id,
        phone_no=phone_no
    )[0]

    return {
        "id": admin_id,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "full_name": full_name,
        "email": email,
        "role": role,
    }


def get_all_admins_service(page: int, limit: int, tenant_id: int | None, role: str | None):
    admins, total = get_all_admins(page=page, limit=limit, tenant_id=tenant_id, role=role)
    return {
        "total": total,
        "admins": admins
    }


def get_admin_by_id_service(id):
    admin = get_admin_by_id(id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

# def get_admins_by_tenant_service(tenant_id):
#     tenant = get_tenant_by_id(tenant_id)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
    
#     admins = get_admins_by_tenant(tenant_id)
#     return {
#         "total": len(admins),
#         "admins": admins
        
#     }


def get_admins_by_tenant_service(tenant_id: str, page: int, limit: int):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    admins, total = get_admins_by_tenant(tenant_id, page=page, limit=limit)
    return {
        "total": total,
        "admins": admins
    }


# def update_admin_service(id, full_name=None, email=None, role=None,is_active=None):
#     admin = get_admin_by_id(id)
#     if not admin:
#         raise HTTPException(status_code=404, detail="Admin not found")
    
#     if email:
#         existing_admin = get_admin_email(email)
#         if existing_admin and existing_admin[0] != id:
#             raise HTTPException(status_code=400, detail="Email already exists")
    
#     success = update_admin(id, full_name, email, role,is_active)
#     if not success:
#         raise HTTPException(status_code=400, detail="No changes made")
    
#     return get_admin_by_id(id)

def update_admin_service(id, full_name=None, role=None, is_active=None):
    admin = get_admin_by_id(id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    success = update_admin(id, full_name, role, is_active)
    if not success:
        raise HTTPException(status_code=400, detail="No changes made")

    return get_admin_by_id(id)



def update_admin_password_service(id, current_password, new_password):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM tenant_admins WHERE id = %s", (id,))
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Admin not found")
            
            stored_password = result[0]
            if not verify_password(current_password, stored_password):
                raise HTTPException(status_code=401, detail="Current password is incorrect")
            
            hashed_password = hash_password(new_password)
            return update_admin_password(id, hashed_password)
    finally:
        db_pool.putconn(conn)

def delete_admin_service(id):
    admin = get_admin_by_id(id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return delete_admin(id)