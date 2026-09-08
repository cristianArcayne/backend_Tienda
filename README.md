# Backend - Atelier Numérique (FastAPI & PostgreSQL)

API RESTful desarrollada con **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL** y autenticación **JWT** con control de roles (RBAC) y bitácora de auditoría.

---

## 🛠️ Requisitos Previos

- Python 3.10 o superior
- PostgreSQL (Base de datos: `bd_tienda_virtual`)

---

## 🚀 Instalación y Ejecución

1. **Crear entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   Copia el archivo `.env.example` a `.env` y ajusta tus credenciales de PostgreSQL si es necesario:
   ```bash
   copy .env.example .env
   ```

4. **Cargar datos iniciales de prueba (Semilla):**
   ```bash
   python seed_data.py
   ```

5. **Iniciar el servidor:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

- **API Base:** `http://localhost:8000`
- **Documentación Interactiva Swagger:** `http://localhost:8000/docs`
- **Documentación ReDoc:** `http://localhost:8000/redoc`

---

## 🧪 Pruebas Automatizadas

Ejecuta el conjunto de pruebas unitarias y de integración:
```bash
python test_api.py
```

---

## 🔑 Credenciales de Prueba

| Rol | Login / CI | Contraseña | Acceso a Bitácora |
| :--- | :--- | :--- | :---: |
| **Administrador** | `1001` | `admin123` |  SÍ |
| **Trabajador** | `2001` | `trabajador123` |  SÍ |
| **Cliente** | `atelier@maison.com` (o `3001`) | `cliente123` |  NO (403 Forbidden) |
