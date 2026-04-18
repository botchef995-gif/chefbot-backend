"""FastAPI main application"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine, Base, get_db
from app.routers import auth, sync
from app import schemas, crud

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

@app.post("/test-register")
def test_register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Endpoint de prueba para registro con detalle de errores"""
    try:
        # Verificar si existe
        existing = crud.get_user_by_email(db, user.email)
        if existing:
            return {"status": "error", "message": "Email ya registrado"}
        
        # Crear usuario
        new_user = crud.create_user(db, user)
        return {
            "status": "success", 
            "user_id": new_user.id,
            "email": new_user.email
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

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
