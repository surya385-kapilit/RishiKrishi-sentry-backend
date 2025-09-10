import math
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.models.tenant_model import get_schema_for_tenant
from app.schema.superadmin_schema import (
    AdminUpdateRequest, SuperAdminLogin, SuperAdminCreate, SuperAdminUpdate, SuperAdminPasswordUpdate,
    SuperAdminResponse, TenantCreate,TenantUpdate, TenantResponse, TenantsWithCountResponse,
    TenantAdminCreate, TenantAdminUpdate, AdminResponse, AdminWithTenantResponse,
    TokenResponse, MessageResponse, SuperAdminDashboardResponse,TenantStatusUpdateResponse,TenantAdminUpdateResponse)
from app.services.superadmin_service import (
    login_superadmin_service, create_superadmin_service, get_all_superadmins_service,
    get_superadmin_by_id_service, update_superadmin_service, 
    delete_superadmin_service, create_tenant_service, get_all_tenants_service,
    get_tenant_by_id_service, update_tenant_service, delete_tenant_service,
    create_tenant_admin_service, get_all_admins_service, get_admin_by_id_service,
    get_admins_by_tenant_service, update_admin_service, delete_admin_service
)
from app.models.superadmin_model import get_superadmin_dashboard_stats
from app.utils.email_sender import send_admin_credentials_email
from app.utils.jwt_token import verify_token
from fastapi.responses import JSONResponse
from fastapi import Request
import httpx
import random
from app.utils import security

SLAVE_API_URL = os.getenv("SLAVE_API_URL")


from app.models.admin_model import delete_admin_in_matrix, get_user_details_from_matrix, save_user_in_matrix_table_with_password, lookup_existing_user_details, update_admin_in_matrix

router = APIRouter(prefix="/api/superadmin", tags=["superadmin"])

# Authentication
@router.post("/login", response_model=TokenResponse)
def login_superadmin(login_data: SuperAdminLogin):
    access_token, refresh_token, role,full_name = login_superadmin_service(login_data.email, login_data.password)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": role,
        "full_name":full_name
        
    }

# Superadmin CRUD Operations
@router.post("/create-superadmin", response_model=SuperAdminResponse)
def create_superadmin(superadmin_data: SuperAdminCreate, user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    superadmin_id = create_superadmin_service(
        superadmin_data.email,
        superadmin_data.password,
        superadmin_data.role,
        superadmin_data.full_name
    )
    superadmin = get_superadmin_by_id_service(superadmin_id)
    print(superadmin)
    return {
        "superadmin_id": superadmin[0],
        "email": superadmin[1],
        "role": superadmin[2],
        "full_name":superadmin[3],
        "created_at": superadmin[4]
    }

@router.get("/all-superadmins", response_model=List[SuperAdminResponse])
def get_all_superadmins(user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    superadmins = get_all_superadmins_service()
    return [
        {
            "superadmin_id": sa[0],
            "email": sa[1],
            "role": sa[2],
            "full_name":sa[3],
            "created_at": sa[4]
        }
        for sa in superadmins
    ]

@router.get("/superadmin/{superadmin_id}", response_model=SuperAdminResponse)
def get_superadmin_by_id(superadmin_id: str, user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    superadmin = get_superadmin_by_id_service(superadmin_id)
    return {
        "superadmin_id": superadmin[0],
        "email": superadmin[1],
        "role": superadmin[2],
        "full_name":superadmin[3],
        "created_at": superadmin[4]
    }

@router.put("/{superadmin_id}")
def update_superadmin(superadmin_id: str, update_data: SuperAdminUpdate, user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    updated = update_superadmin_service(
        superadmin_id,
        full_name=update_data.full_name
    )

    return {
        "message": "Superadmin updated successfully"
        # "updated_details": {
        #     "full_name": updated[3],
        #     "role":updated[2] 
        # }
    }



@router.delete("/{superadmin_id}", response_model=MessageResponse)
def delete_superadmin(superadmin_id: str, user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    delete_superadmin_service(superadmin_id)
    return {"message": "Superadmin deleted successfully"}

# Tenant CRUD Operations
@router.post("/create-tenants", response_model=TenantResponse)
def create_tenant(tenant_data: TenantCreate,request:Request ,user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    auth_header = request.headers.get("Authorization")
    
    tenant_id = create_tenant_service(tenant_data.tenant_name, tenant_data.tenant_domain,auth_header)
    tenant = get_tenant_by_id_service(tenant_id)
    
    return {
        "tenant_id": tenant[0],
        "tenant_name": tenant[1],
        "tenant_domain": tenant[2],
        "schema_id": tenant[3],
        "is_active": tenant[4],
        "created_at": tenant[5]
    }

@router.get("/tenants", response_model=TenantsWithCountResponse)
def get_all_tenants(user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    tenants = get_all_tenants_service()
    
    tenant_list = [
        {
            "tenant_id": t[0],
            "tenant_name": t[1],
            "tenant_domain": t[2],
            "schema_id": t[3],
            "is_active": t[4],
            "created_at": t[5]
        }
        for t in tenants
    ]
    
    return {
        "total_tenants": len(tenant_list),
        "tenants": tenant_list
    }

@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
def get_tenant_by_id(tenant_id: str, user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    tenant = get_tenant_by_id_service(tenant_id)
    return {
        "tenant_id": tenant[0],
        "tenant_name": tenant[1],
        "tenant_domain": tenant[2],
        "schema_id": tenant[3],
        "is_active": tenant[4],
        "created_at": tenant[5]
    }


@router.put("/tenants/{tenant_id}")
def update_tenant(tenant_id: str, update_data: TenantUpdate, user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    tenant = update_tenant_service(
        tenant_id=tenant_id,
        is_active=update_data.is_active
    )

    return {
        "message": "Tenant status updated successfully",
        "tenant_name": tenant[1],   # assuming index 1 is tenant_name
        "is_active": tenant[4]      # assuming index 4 is is_active
    }

@router.delete("/tenants/{tenant_id}", response_model=MessageResponse)
def delete_tenant(tenant_id: str, user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    delete_tenant_service(tenant_id)
    return {"message": "Tenant deleted successfully"}

# Admin CRUD Operations
@router.post("/create-admin", response_model=AdminResponse)
async def create_admin(req: Request):
    """
    Creates an admin user.
    1. Creates the user in the remote 'slave' service.
    2. If successful, creates or updates the user's record in the central 'matrix' table.
    """
    # 1. Parse the request body
    try:
        request_data = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body provided.")

    tenant_id = request_data.get("tenant_id")
    full_name = request_data.get("full_name")
    email = request_data.get("email")
    phone = request_data.get("phone")

    # Validate essential data
    if not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required.")
    if not full_name:
        raise HTTPException(status_code=400, detail="full_name is required.")
    if not email:
        raise HTTPException(status_code=400, detail="email is required.")
    if not phone:
        raise HTTPException(status_code=400, detail="phone is required.")

    # 2. Get schema_id from DB using tenant_id
    try:
        schema_id = get_schema_for_tenant(tenant_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"No schema found for tenant_id: {tenant_id}")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch schema_id for tenant.")

    admin_data = {
        "tenant_id": tenant_id,
        "schema_id": schema_id,  # Now retrieved from DB
        "full_name": full_name,
        "email": email,
        "phone": phone,
    }

    # 3. Call SLAVE API to create admin
    auth_header = req.headers.get("Authorization")
    async with httpx.AsyncClient() as client:
        try:
            admin_created_response = await client.post(
                f"{SLAVE_API_URL}/api/external/create-admin",
                json={
                    "schema_id": schema_id,
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "role": "ADMIN",
                },
                headers={"Authorization": auth_header},
                timeout=30.0,
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Could not connect to slave service: {e}")

    # 4. Handle SLAVE API response
    if admin_created_response.status_code in [200, 201]:
        slave_response_data = admin_created_response.json()
        user_id = slave_response_data.get("user_id")
        role = slave_response_data.get("role", "ADMIN")

        if not user_id:
            return JSONResponse(status_code=500, content={"message": "Slave service returned success but no user_id."})

        # Check if user exists globally
        password, _, _, exists = lookup_existing_user_details(email, phone)
        if exists:
            hashed_password = password
        else:
            new_password_plain = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=12))
            print("new_password_plain",new_password_plain)
            hashed_password = security.hash_password(new_password_plain)
            tenant_name=get_tenant_by_id_service(tenant_id)[1]
            try:
                await send_admin_credentials_email(
                    full_name=full_name,
                    email=email,
                    password=new_password_plain,
                    tenant_name=tenant_name,  # You might want to fetch actual tenant_name here
                    role=role
                )
            except HTTPException as e:
                print(f"[WARNING] Failed to send email to {email}: {e.detail}")

        # Save to matrix table
        saved = save_user_in_matrix_table_with_password(
            user_id=user_id,
            tenant_id=tenant_id,
            full_name=full_name,
            email=email,
            phone=phone,
            password=hashed_password,
            role="ADMIN",
        )

        if saved:
            return JSONResponse(status_code=201, content={"message": "Admin created successfully.", "user_id": user_id, "name": full_name, "email": email})
        else:
            return JSONResponse(status_code=500, content={"message": "Failed to save user in matrix after slave success."})
    else:
        return JSONResponse(status_code=admin_created_response.status_code, content={"message": "Failed to create admin on slave.", "detail": admin_created_response.json()})


@router.get("/users")
def get_all_admins(
    user: dict = Depends(verify_token),
    page: int = Query(0, ge=0, description="Page number (starts from 0)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    tenant_id: int | None = Query(None, description="Filter by tenant_id"),
    role: str | None = Query(None, description="Filter by role")
):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    result = get_all_admins_service(page=page, limit=limit, tenant_id=tenant_id, role=role)

    return {
        "total_admins": result["total"],
        "page": page,
        "limit": limit,
        "admins": [
            {
                "id": admin["id"],
                "user_id": admin["user_id"],
                "tenant_id": admin["tenant_id"],
                "full_name": admin["full_name"],
                "email": admin["email"],
                "role": admin["role"],
                "is_active": admin["is_active"],
                "tenant_name": admin["tenant_name"],
                "created_at": admin["created_at"],
            }
            for admin in result["admins"]
        ]
    }


@router.get("/users/{id}", response_model=AdminResponse)
def get_admin_by_id(id: int, user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    admin = get_admin_by_id_service(id)
    return {
        "id": admin["id"],
        "user_id": admin["user_id"],
        "tenant_id": admin["tenant_id"],
        "full_name": admin["full_name"],
        "email": admin["email"],
        "role": admin["role"],
        "is_active": admin["is_active"],
        "tenant_name": admin["tenant_name"],
        "created_at": admin["created_at"],
        # "updated_at": admin["updated_at"],
        # "schema_id": admin["schema_id"]
    }

@router.get("/{tenant_id}/users")
def get_admins_by_tenant(
    tenant_id: str,
    user: dict = Depends(verify_token),
    page: int = Query(0, ge=0, description="Page number (starts from 0)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = get_admins_by_tenant_service(tenant_id, page=page, limit=limit)
    total=result["total"]
    total_pages = math.ceil(total / limit) if limit else 0

    return {
        
        "page": page,
        "limit": limit,
        "total_users": result["total"],
        "total_pages": total_pages,
        "users": [
            {
                "id": admin["id"],
                "user_id": admin["user_id"],
                "tenant_id": admin["tenant_id"],
                "full_name": admin["full_name"],
                "email": admin["email"],
                "role": admin["role"],
                "is_active": admin["is_active"],
                "tenant_name": admin["tenant_name"],
                "created_at": admin["created_at"],
            }
            for admin in result["admins"]
        ],
    }


@router.put("/users/update/{user_id}")
async def update_admin_handler(user_id: str, body: AdminUpdateRequest,request: Request):
    """
    1. Send update request to Slave service
    2. On success, update the central matrix table
    """
    # Extract Authorization header from incoming request
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    tenant_id = body.tenant_id
        # 2. Get schema_id from DB using tenant_id
    try:
        schema_id = get_schema_for_tenant(tenant_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"No schema found for tenant_id: {tenant_id}")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch schema_id for tenant.")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{SLAVE_API_URL}/api/external/update-admin/{user_id}",
                json={
                    "schema_id": schema_id,
                    "full_name": body.full_name,
                    "status": body.status
                },
                headers={
                    "Authorization": auth_header},
                timeout=30.0
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error contacting slave: {e}")

    if response.status_code not in [200, 201]:
        return {
            "message": "Failed to update admin on slave",
            "detail": response.json()
        }

    # Convert 'status' to is_active
    is_active = True if body.status == "active" else False

    # Update matrix table (central DB)
    updated = update_admin_in_matrix(
        user_id=user_id,
        tenant_id=body.tenant_id,
        full_name=body.full_name,
        is_active=is_active
    )

    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update admin in matrix table")

    return {
        "message": "User updated successfully in both systems.",
        "user_id": user_id,
        "full_name": body.full_name,
        "is_active": is_active
    }



##Delete the Admin from matrix table
@router.delete("/users/delete/{user_id}")
async def delete_admin_handler(user_id: str,request: Request):
    # 1. Lookup from matrix
    user_data = get_user_details_from_matrix(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found in matrix")

    tenant_id = user_data["tenant_id"]
    schema_id = get_schema_for_tenant(tenant_id)  # You should already have this mapping in DB or cache
    # Extract Authorization header from incoming request
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    # 2. Delete from slave
    try:
        async with httpx.AsyncClient() as client:
            slave_response = await client.delete(
                f"{SLAVE_API_URL}/api/external/delete-admin/{user_id}",
                params={"schema_id": schema_id},
                    headers={
                    "Authorization": auth_header # Replace with actual token
                },
                timeout=20.0
            )
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error contacting slave: {e}")

    if slave_response.status_code not in [200, 204]:
        return {
            "message": "Failed to delete admin from slave",
            "detail": slave_response.json()
        }

    # 3. Delete from matrix
    deleted = delete_admin_in_matrix(user_id=user_id, tenant_id=tenant_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete admin from matrix")

    return {"message": "Admin deleted from both slave and matrix", "user_id": user_id}

# Get Dashboard
@router.get("/dashboard", response_model=SuperAdminDashboardResponse)
def get_superadmin_dashboard(user: dict = Depends(verify_token)):
    if user["role"].upper() != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return get_superadmin_dashboard_stats()