from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.bitacora import router as bitacora_router
from app.api.usuarios import router as usuarios_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API RESTful para Atelier Numérique con RBAC (Admin, Trabajador, Cliente), Bitácora de Auditoría y soporte para Web y Móvil."
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(auth_router, prefix="/api")
app.include_router(bitacora_router, prefix="/api")
app.include_router(usuarios_router, prefix="/api")

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
