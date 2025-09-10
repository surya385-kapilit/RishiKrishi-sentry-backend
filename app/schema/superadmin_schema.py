from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from typing import Literal
# Base Response Models  
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    role: str
    full_name:str

class MessageResponse(BaseModel):
    message: str

# Superadmin Schemas
class SuperAdminLogin(BaseModel):
    email: EmailStr
    password: str

class SuperAdminCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
    full_name: str

class SuperAdminUpdate(BaseModel):  
    full_name: str

class SuperAdminPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class SuperAdminResponse(BaseModel):
    superadmin_id: int
    email: EmailStr
    role: str
    full_name: Optional[str]
    created_at: datetime

# Tenant Schemas
class TenantCreate(BaseModel):
    tenant_name: str
    tenant_domain: str


#Update Tenant
class TenantUpdate(BaseModel):
    is_active: bool

class TenantStatusUpdateResponse(BaseModel):
    message: str
    tenant_name: str
    is_active: bool


class TenantResponse(BaseModel):
    tenant_id: str
    tenant_name: str
    tenant_domain: str
    schema_id: Optional[str]
    is_active: bool
    created_at: datetime

class TenantsWithCountResponse(BaseModel):
    total_tenants: int
    tenants: list[TenantResponse]

# Admin Schemas
class TenantAdminCreate(BaseModel):
    tenant_id: str
    full_name: str
    email: EmailStr
    role: str
    phone_no: Optional[str] = None
    is_active: bool = True

##Update Admin in matrix 

class AdminUpdateRequest(BaseModel):
    tenant_id: str
    # schema_id: str
    full_name: str
    status: Literal["active", "inactive"]

# class TenantAdminUpdate(BaseModel):
#     full_name: Optional[str] = None
#     # email: Optional[EmailStr] = None
#     role: Optional[str] = None
#     is_active: Optional[bool] = None

# class TenantAdminUpdateResponse(BaseModel):
#     message: str
#     tenant_admin_id: int
#     full_name: Optional[str] = None
#     email: Optional[EmailStr] = None
#     role: Optional[str] = None
#     is_active: Optional[bool] = None


class TenantAdminUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class TenantAdminUpdateResponse(BaseModel):
    message: str
    tenant_admin_id: int
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None




class TenantAdminPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class AdminResponse(BaseModel):
    id: int
    user_id: str
    tenant_id: str
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    tenant_name: str
    created_at: datetime
    # updated_at: datetime
    # schema_id: Optional[str]
    

class AdminWithTenantResponse(BaseModel):
    id: int
    user_id: str
    tenant_id: str
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    tenant_name: str
    created_at: datetime
    # updated_at: datetime
    # schema_id: Optional[str]

# Get Dashboard
class SuperAdminDashboardResponse(BaseModel):
    total_tenants: int
    active_tenants: int
    total_users: int