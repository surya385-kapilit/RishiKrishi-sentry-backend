
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Login Schema for Admins
class AdminLogin(BaseModel):
    # email:Optional[EmailStr] = None
    # phone: Optional[str] = None
    user_name: str
    password: str
    
class TenantLogin(BaseModel):
    tenant_id: str
    # email: Optional[EmailStr] = None
    # phone: Optional[str] = None
    user_name: Optional[str] = None 
    password: Optional[str] = None

class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token:str 
    user_id: str  
    full_name: str
    tenant_name: str
    role: str
    
    # is_active: bool
    
    # tenant_id: str
    # schema_id: Optional[str]
    # email: EmailStr
    
    
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    
class CreateUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    role: str

class UpdateUserRequest(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]

class UserResponse(BaseModel):
    id: int
    user_id: str
    tenant_id: str
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: str
    updated_at: Optional[str]
    tenant_name: str
    schema_id: str
