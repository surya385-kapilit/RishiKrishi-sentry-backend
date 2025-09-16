# supervisor_router.py
from fastapi import APIRouter, HTTPException
from app.schema.admin_schema import AdminLogin, AdminLoginResponse, TenantLogin
from app.services.admin_service import login_admin_step_one, login_admin_step_two
from app.services.supervisor_service import login_supervisor_service
from app.schema.supervisor_schema import SupervisorLogin, SupervisorLoginResponse

router = APIRouter(prefix="/api/auth", tags=["Supervisor"])


@router.post("/login")
def login_step_one(login_data: AdminLogin):
    try:
        return login_admin_step_one(login_data.email, login_data.phone, login_data.password)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/tenant-login", response_model=AdminLoginResponse)
def tenant_login(login_data: TenantLogin):
    try:
        return login_admin_step_two(
            tenant_id=login_data.tenant_id,
            email=login_data.email,
            phone=login_data.phone,
            password=login_data.password
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
