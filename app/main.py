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

@app.get("/init-db")
def init_database():
    """Inicializa la base de datos (solo para setup inicial)"""
    try:
        Base.metadata.create_all(bind=engine)
        return {"status": "success", "message": "Tablas creadas correctamente"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/debug-db")
def debug_database():
    """Debug de conexión a base de datos"""
    from app.config import get_settings
    settings = get_settings()
    
    db_url = settings.database_url
    # Ocultar contraseña
    if "@" in db_url:
        parts = db_url.split("@")
        db_url_masked = parts[0].split(":")[0] + ":***@" + parts[1]
    else:
        db_url_masked = db_url
    
    try:
        # Probar conexión
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            conn.commit()
        return {
            "database_url": db_url_masked,
            "connection": "OK",
            "tables_created": True
        }
    except Exception as e:
        return {
            "database_url": db_url_masked,
            "connection": "FAILED",
            "error": str(e)
        }
