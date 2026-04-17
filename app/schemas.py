"""Pydantic schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date

# ============== AUTH SCHEMAS ==============

class UserBase(BaseModel):
    email: EmailStr
    nombre: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    last_sync: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

# ============== INVENTARIO SCHEMAS ==============

class InventarioItemBase(BaseModel):
    ingrediente_nombre: str
    cantidad: float = 1
    unidad: str = "pieza"
    categoria: Optional[str] = None
    fecha_compra: date
    fecha_caducidad: date
    notas: Optional[str] = None

class InventarioItemCreate(InventarioItemBase):
    pass

class InventarioItem(InventarioItemBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InventarioSync(BaseModel):
    items: List[InventarioItem]
    last_sync: Optional[datetime] = None

# ============== RECETAS SCHEMAS ==============

class RecetaGuardadaBase(BaseModel):
    fuente: str = "manual"
    spoonacular_id: Optional[int] = None
    url_original: Optional[str] = None
    titulo: str
    descripcion: Optional[str] = None
    instrucciones: Optional[str] = None
    tiempo_preparacion: int = 0
    tiempo_coccion: int = 0
    porciones: int = 0
    imagen_url: Optional[str] = None
    ingredientes: Optional[List[str]] = None

class RecetaGuardadaCreate(RecetaGuardadaBase):
    pass

class RecetaGuardada(RecetaGuardadaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RecetasSync(BaseModel):
    recetas: List[RecetaGuardada]
    last_sync: Optional[datetime] = None

# ============== SYNC SCHEMAS ==============

class SyncStatus(BaseModel):
    user_id: int
    last_sync: Optional[datetime]
    inventario_count: int
    recetas_count: int
    device_id: Optional[str] = None

class SyncRequest(BaseModel):
    device_id: Optional[str] = None
    inventario: Optional[List[InventarioItemCreate]] = None
    recetas: Optional[List[RecetaGuardadaCreate]] = None

class SyncResponse(BaseModel):
    status: str
    message: str
    inventario_synced: int = 0
    recetas_synced: int = 0
    server_timestamp: datetime
