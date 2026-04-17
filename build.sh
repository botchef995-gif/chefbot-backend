#!/bin/bash

# Script de build para Render
pip install -r requirements.txt

# Crear tablas en la base de datos
python3 -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine); print('Tablas creadas')"
