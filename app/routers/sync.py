"""Sync router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app import schemas, crud, models
from app.auth import get_current_active_user
from app.database import get_db

router = APIRouter(prefix="/sync", tags=["sync"])

@router.get("/status", response_model=schemas.SyncStatus)
def get_sync_status(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene estado de sincronización del usuario"""
    inventario_count = len(crud.get_inventario(db, current_user.id))
    recetas_count = len(crud.get_recetas_guardadas(db, current_user.id))
    
    return schemas.SyncStatus(
        user_id=current_user.id,
        last_sync=current_user.last_sync,
        inventario_count=inventario_count,
        recetas_count=recetas_count
    )

@router.get("/inventario", response_model=schemas.InventarioSync)
def get_inventario(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene inventario sincronizado del usuario"""
    items = crud.get_inventario(db, current_user.id)
    
    return schemas.InventarioSync(
        items=items,
        last_sync=current_user.last_sync
    )

@router.post("/inventario", response_model=schemas.SyncResponse)
def sync_inventario(
    data: schemas.InventarioSync,
    device_id: str = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sincroniza inventario del usuario"""
    try:
        count = crud.sync_inventario(db, current_user.id, data.items)
        crud.update_last_sync(db, current_user.id)
        
        # Log
        crud.create_sync_log(
            db, current_user.id, device_id, "inventario", "success", count
        )
        
        return schemas.SyncResponse(
            status="success",
            message=f"Inventario sincronizado: {count} items",
            inventario_synced=count,
            server_timestamp=datetime.utcnow()
        )
    except Exception as e:
        crud.create_sync_log(
            db, current_user.id, device_id, "inventario", "error", error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sincronizando inventario: {str(e)}"
        )

@router.get("/recetas", response_model=schemas.RecetasSync)
def get_recetas(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene recetas guardadas del usuario"""
    recetas = crud.get_recetas_guardadas(db, current_user.id)
    
    return schemas.RecetasSync(
        recetas=recetas,
        last_sync=current_user.last_sync
    )

@router.post("/recetas", response_model=schemas.SyncResponse)
def sync_recetas(
    data: schemas.RecetasSync,
    device_id: str = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sincroniza recetas del usuario"""
    try:
        count = crud.sync_recetas(db, current_user.id, data.recetas)
        crud.update_last_sync(db, current_user.id)
        
        # Log
        crud.create_sync_log(
            db, current_user.id, device_id, "recetas", "success", count
        )
        
        return schemas.SyncResponse(
            status="success",
            message=f"Recetas sincronizadas: {count} nuevas",
            recetas_synced=count,
            server_timestamp=datetime.utcnow()
        )
    except Exception as e:
        crud.create_sync_log(
            db, current_user.id, device_id, "recetas", "error", error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sincronizando recetas: {str(e)}"
        )

@router.post("/full", response_model=schemas.SyncResponse)
def sync_full(
    data: schemas.SyncRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sincronización completa (inventario + recetas)"""
    inv_count = 0
    rec_count = 0
    
    try:
        # Sync inventario
        if data.inventario:
            inv_count = crud.sync_inventario(db, current_user.id, data.inventario)
        
        # Sync recetas
        if data.recetas:
            rec_count = crud.sync_recetas(db, current_user.id, data.recetas)
        
        # Update timestamp
        crud.update_last_sync(db, current_user.id)
        
        # Log
        crud.create_sync_log(
            db, current_user.id, data.device_id, "full", "success", 
            inv_count + rec_count
        )
        
        return schemas.SyncResponse(
            status="success",
            message=f"Sincronización completa exitosa",
            inventario_synced=inv_count,
            recetas_synced=rec_count,
            server_timestamp=datetime.utcnow()
        )
    except Exception as e:
        crud.create_sync_log(
            db, current_user.id, data.device_id, "full", "error", error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en sincronización: {str(e)}"
        )
