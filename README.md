# ChefBot Backend - FastAPI + PostgreSQL

Backend para sincronización de ChefBot entre dispositivos.

## 🚀 Deploy en Render

1. Crear nuevo Web Service
2. Conectar repositorio de GitHub (o subir manualmente)
3. Configurar variables de entorno:
   - `DATABASE_URL` (de PostgreSQL en Render)
   - `SECRET_KEY` (generar uno seguro)
   - `ALGORITHM` = "HS256"
   - `ACCESS_TOKEN_EXPIRE_MINUTES` = "30"

4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 📁 Estructura

```
chefbot-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── database.py      # Conexión PostgreSQL
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── auth.py          # JWT auth
│   ├── crud.py          # Operaciones DB
│   └── sync.py          # Lógica de sincronización
├── alembic/             # Migraciones
├── requirements.txt
└── README.md
```

## 🔌 API Endpoints

### Auth
- `POST /auth/register` - Crear cuenta
- `POST /auth/login` - Iniciar sesión

### Sync
- `GET /sync/inventario` - Obtener inventario
- `POST /sync/inventario` - Subir inventario
- `GET /sync/recetas` - Obtener recetas guardadas
- `POST /sync/recetas` - Subir recetas
- `GET /sync/status` - Estado de sincronización
