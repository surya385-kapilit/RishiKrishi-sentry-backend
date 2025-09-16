from fastapi import APIRouter, Depends, HTTPException, Query
from app.schema.admin_schema import AdminLogin, AdminLoginResponse, ChangePasswordRequest, CreateUserRequest, TenantLogin
from app.services.admin_service import change_admin_password_service, login_admin_step_one, login_admin_step_two
from app.services.superadmin_service import create_tenant_admin_service
from app.utils.jwt_token import verify_admin_token
from app.models.admin_model import get_admin_by_id, get_admins_by_tenant,delete_admin, get_all_tenants_by_email,update_admin
from app.schema.admin_schema import UpdateUserRequest
router = APIRouter(prefix="/api", tags=["admin"])


@router.post("/auth/login")
def login_step_one(login_data: AdminLogin):
    try:
        return login_admin_step_one(login_data.user_name, login_data.password)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/auth/tenant-login", response_model=AdminLoginResponse)
def tenant_login(login_data: TenantLogin):
    try:
        return login_admin_step_two(
            tenant_id=login_data.tenant_id,
            # email=login_data.email,
            # phone=login_data.phone,
            user_name=login_data.user_name,
            password=login_data.password
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")




@router.post("/auth/change-password", summary="Change Admin Password")
def change_password(
    data: ChangePasswordRequest,
    token_data: dict = Depends(verify_admin_token)
):
    try:
        print("Token Data:", token_data)
        message = change_admin_password_service(
            tenant_id=token_data["tenant_id"],
            email=token_data["email"],
            old_password=data.old_password,
            new_password=data.new_password
        )
        return {"message": message}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

@router.delete("/users/{user_id}", summary="Delete user")
def delete_user(user_id: int, token_data: dict = Depends(verify_admin_token)):
    try:
        user = get_admin_by_id(user_id)
        if not user or user["tenant_id"] != token_data["tenant_id"]:
            raise HTTPException(status_code=404, detail="User not found or unauthorized")

        deleted = delete_admin(user_id)
        if not deleted:
            raise HTTPException(status_code=400, detail="User deletion failed")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/tenant-list", summary="Get all tenants for the admin")
def get_tenants(
    email: str = Query(..., description="Admin email to fetch tenants")):
    try:
        tenants = get_all_tenants_by_email(email)
        if not tenants:
            raise HTTPException(status_code=404, detail="No tenants found")
        return {"tenants": tenants}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    


