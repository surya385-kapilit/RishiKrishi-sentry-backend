# schemas/supervisor_schema.py
from pydantic import BaseModel

class SupervisorLogin(BaseModel):
    email: str
    password: str

class SupervisorLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    full_name: str
    tenant_name: str
    # email: str
    # is_active: bool
    
