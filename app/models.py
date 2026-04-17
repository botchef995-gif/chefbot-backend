"""SQLAlchemy models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    """Usuario de ChefBot"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nombre = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime, nullable=True)
    
    # Relaciones
    inventario = relationship("InventarioItem", back_populates="user", cascade="all, delete-orphan")
    recetas_guardadas = relationship("RecetaGuardada", back_populates="user", cascade="all, delete-orphan")

class InventarioItem(Base):
    """Item en el inventario del usuario"""
    __tablename__ = "inventario"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ingrediente_nombre = Column(String, nullable=False)
    cantidad = Column(Float, default=1)
    unidad = Column(String, default="pieza")
    categoria = Column(String)
    fecha_compra = Column(Date, nullable=False)
    fecha_caducidad = Column(Date, nullable=False)
    notas = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="inventario")

class RecetaGuardada(Base):
    """Receta guardada por el usuario"""
    __tablename__ = "recetas_guardadas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Fuente
    fuente = Column(String)  # 'local', 'spoonacular', 'web', 'manual'
    spoonacular_id = Column(Integer, nullable=True)
    url_original = Column(String, nullable=True)
    
    # Datos de la receta
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    instrucciones = Column(Text)
    tiempo_preparacion = Column(Integer, default=0)
    tiempo_coccion = Column(Integer, default=0)
    porciones = Column(Integer, default=0)
    imagen_url = Column(String)
    
    # JSON con ingredientes
    ingredientes_json = Column(Text)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="recetas_guardadas")

class SyncLog(Base):
    """Log de sincronizaciones"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String)  # Identificador del dispositivo
    sync_type = Column(String)  # 'inventario', 'recetas', 'full'
    status = Column(String)  # 'success', 'error'
    items_synced = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
