"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.routers import auth, sync

settings = get_settings()

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear app
app = FastAPI(
    title=settings.app_name,
    description="Backend API para sincronización de ChefBot",
    version="1.0.0"
)

# CORS (para permitir requests desde el desktop app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(sync.router)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "ChefBot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
