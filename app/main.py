from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.supervisor_router import router as supervisor_router
from app.routes.superadmin_routes import router as superadmin_router
from app.routes.admin_routes import router as admin_router
from app.routes.auth_routes import router as auth_router

from app.routes.external.external_router import router as external_router


app = FastAPI(
    title="Multi-Tenant Management System",
    description="A comprehensive multi-tenant management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(auth_router, prefix="/auth")


# Include routers
app.include_router(superadmin_router)
app.include_router(admin_router)
app.include_router(supervisor_router)
app.include_router(auth_router, prefix="/api/auth")
app.include_router(external_router)

@app.get("/")
def read_root():
    return {"message": "Multi-Tenant Management System API"}

# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)