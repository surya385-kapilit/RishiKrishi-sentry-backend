
from pydantic import BaseModel, EmailStr
from typing import Optional
class UserCreateSchema(BaseModel):
    email: EmailStr
    name: str
    role: str
    phone: str

class UserCreateResponseSchema(BaseModel):
    message: str
    user_id: str
    name: str
    email: str
    role: str

class UserUpdateSchema(BaseModel):
    email:Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None  
    phone: Optional[str] = None
    is_active: Optional[bool] = None    