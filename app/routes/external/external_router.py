
from fastapi import APIRouter, Request, HTTPException, Depends
from app.models.users_model import create_matrix_user, delete_matrix_user, update_matrix_user
from app.schema.users_schema import UserCreateSchema, UserCreateResponseSchema, UserUpdateSchema
from app.utils.email_sender import send_admin_credentials_email
from app.utils.jwt_token import verify_admin_token
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/external", tags=["external"])

# @router.post("/create-user", response_model=UserCreateResponseSchema)
# def create_user_from_slave(
#     user_data: UserCreateSchema,
#     user: dict = Depends(verify_admin_token)  # validates JWT and extracts tenant info
# ):
#     tenant_id = user.get("tenant_id")
#     if not tenant_id:
#         raise HTTPException(status_code=400, detail="Tenant ID missing from token")

#     try:
#         user_id = create_matrix_user(
#             email=user_data.email,
#             full_name=user_data.name,
#             role=user_data.role,
#             phone_no=user_data.phone,
#             tenant_id=tenant_id
#         )

#         return JSONResponse(
#             status_code=201,
#             content={
#                 "message": "User created successfully",
#                 "user_id": user_id,
#                 "name": user_data.name,
#                 "email": user_data.email,
#                 "role": user_data.role
#             }
#         )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create user: {e}")

@router.post("/create-user", response_model=UserCreateResponseSchema)
async def create_user_from_slave(
    user_data: UserCreateSchema,
    user: dict = Depends(verify_admin_token)
):
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID missing from token")

    try:
        user_id, exists, new_password_plain,tenant_name= create_matrix_user(
            email=user_data.email,
            full_name=user_data.name,
            role=user_data.role,
            phone_no=user_data.phone,
            tenant_id=tenant_id,
            
        )

        # Send credentials only for new users
        if not exists and new_password_plain:
            try:
                await send_admin_credentials_email(
                    full_name=user_data.name,
                    email=user_data.email,
                    password=new_password_plain,
                    tenant_name=tenant_name,
                    role=user_data.role,
                    is_new_user=True
                )
            except Exception as e:
                print(f"[WARNING] Failed to send email to {user_data.email}: {e}")

        return JSONResponse(
            status_code=201,
            content={
                "message": "User created successfully",
                "user_id": user_id,
                "name": user_data.name,
                "email": user_data.email,
                "role": user_data.role
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {e}")



@router.put("/update-user/{user_id}")
def update_user_from_slave(
    user_id: str,
    user_data: UserUpdateSchema,
    user: dict = Depends(verify_admin_token)
):
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID missing from token")
    
    print("user_data",user_data)

    try:
        update_matrix_user(
            user_id=user_id,
            email=user_data.email,
            full_name=user_data.name,
            role=user_data.role,
            phone_no=user_data.phone,
            is_active=user_data.is_active,
            tenant_id=tenant_id
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "User updated successfully",
                "user_id": user_id,
                "name": user_data.name,
                "email": user_data.email,
                "role": user_data.role,
                "phone": user_data.phone,
                "is_active": user_data.is_active
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {e}")
    
@router.delete("/delete-user/{user_id}")
def delete_user_from_slave(
    user_id: str,
    user: dict = Depends(verify_admin_token)
):
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID missing from token")

    try:
        delete_matrix_user(user_id, tenant_id)
        return JSONResponse(
            status_code=200,
            content={"message": "User deleted successfully", "user_id": user_id}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {e}")