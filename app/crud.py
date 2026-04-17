"""CRUD operations"""
from sqlalchemy.orm import Session
from typing import Optional, List
import json
from datetime import datetime

from app import models, schemas
from app.auth import get_password_hash

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Obtiene usuario por email"""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Crea nuevo usuario"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        nombre=user.nombre
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_last_sync(db: Session, user_id: int):
    """Actualiza timestamp de última sync"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.last_sync = datetime.utcnow()
        db.commit()

# ============== INVENTARIO CRUD ==============

def get_inventario(db: Session, user_id: int) -> List[models.InventarioItem]:
    """Obtiene inventario del usuario"""
    return db.query(models.InventarioItem).filter(
        models.InventarioItem.user_id == user_id
    ).all()

def sync_inventario(
    db: Session, 
    user_id: int, 
    items: List[schemas.InventarioItemCreate]
) -> int:
    """Sincroniza inventario (reemplaza todo)"""
    # Eliminar items existentes
    db.query(models.InventarioItem).filter(
        models.InventarioItem.user_id == user_id
    ).delete()
    
    # Crear nuevos items
    for item_data in items:
        db_item = models.InventarioItem(
            user_id=user_id,
            **item_data.model_dump()
        )
        db.add(db_item)
    
    db.commit()
    return len(items)

# ============== RECETAS CRUD ==============

def get_recetas_guardadas(db: Session, user_id: int) -> List[models.RecetaGuardada]:
    """Obtiene recetas guardadas del usuario"""
    return db.query(models.RecetaGuardada).filter(
        models.RecetaGuardada.user_id == user_id
    ).all()

def sync_recetas(
    db: Session,
    user_id: int,
    recetas: List[schemas.RecetaGuardadaCreate]
) -> int:
    """Sincroniza recetas (merge - no borra existentes)"""
    count = 0
    
    for receta_data in recetas:
        # Buscar si ya existe
        existing = db.query(models.RecetaGuardada).filter(
            models.RecetaGuardada.user_id == user_id,
            models.RecetaGuardada.titulo == receta_data.titulo
        ).first()
        
        if existing:
            # Actualizar
            for key, value in receta_data.model_dump().items():
                if key == "ingredientes":
                    setattr(existing, "ingredientes_json", json.dumps(value))
                else:
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
        else:
            # Crear nueva
            ingredientes = receta_data.ingredientes
            db_receta = models.RecetaGuardada(
                user_id=user_id,
                **receta_data.model_dump(exclude={"ingredientes"})
            )
            if ingredientes:
                db_receta.ingredientes_json = json.dumps(ingredientes)
            db.add(db_receta)
            count += 1
    
    db.commit()
    return count

# ============== SYNC LOG ==============

def create_sync_log(
    db: Session,
    user_id: int,
    device_id: Optional[str],
    sync_type: str,
    status: str,
    items_synced: int = 0,
    error_message: Optional[str] = None
):
    """Crea registro de sincronización"""
    log = models.SyncLog(
        user_id=user_id,
        device_id=device_id,
        sync_type=sync_type,
        status=status,
        items_synced=items_synced,
        error_message=error_message
    )
    db.add(log)
    db.commit()
