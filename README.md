# 📦 Sistema de Gestión de Encomiendas

Proyecto desarrollado con **Django + Docker + PostgreSQL** para la gestión de envíos de encomiendas, clientes y rutas.

---

## 🚀 Tecnologías utilizadas

- Python 3.11
- Django
- PostgreSQL
- Docker & Docker Compose
- python-decouple

---

## 📁 Estructura del proyecto

encomiendas/
│
├── config/ # Configuración del proyecto Django
├── envios/ # App de gestión de encomiendas
├── clientes/ # App de clientes
├── rutas/ # App de rutas
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── manage.py


---

## ⚙️ Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/MrCale26/encomiendas.git
cd encomiendas


2. Crear archivo .env

Crear un archivo .env en la raíz del proyecto:

SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=encomiendas_db
DB_USER=encomiendas_user
DB_PASSWORD=encomiendas_pass_2026
DB_HOST=db
DB_PORT=5432


3. Construir y levantar contenedores
docker compose up --build -d



4. Aplicar migraciones
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate


5. Crear superusuario
docker compose exec web python manage.py createsuperuser


🌐 Acceso al sistema
Aplicación web: http://localhost:8000
Panel admin: http://localhost:8000/admin


📊 Funcionalidades
Registro de encomiendas
Gestión de clientes
Administración de rutas
Control de estados de envío:
Pendiente
En tránsito
Entregado
Devuelto


🐳 Docker

El proyecto está completamente containerizado:

web: aplicación Django
db: base de datos PostgreSQL


🔐 Seguridad
Variables sensibles en .env
.env excluido del repositorio (.gitignore)
Uso de python-decouple



👨‍💻 Autor
Desarrollado por: MrCale

📌 Notas
Este proyecto fue desarrollado como parte de un taller de Django para aprendizaje de:
Arquitectura MVT
Uso de Docker en desarrollo
Integración con PostgreSQL