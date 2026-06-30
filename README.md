# cert-backend

Backend (API REST) para la reserva y gestión de **auditorías ISO** (Internas, MINTRA y Externas de Certificación). Construido con **Django + Django REST Framework + PostgreSQL**.

> Solo backend. El frontend es responsabilidad de otro equipo y consume esta API.

## Documentación

- [`docs/scope.md`](docs/scope.md) — alcance del proyecto.
- [`docs/architecture.md`](docs/architecture.md) — arquitectura y estructura de capas.
- [`docs/database-schema.md`](docs/database-schema.md) — esquema de la base de datos.

## Stack

Python 3.x · Django 5 · DRF · PostgreSQL · JWT (SimpleJWT) · Swagger/OpenAPI (drf-spectacular) · Docker.

## Módulos (apps)

| App | Responsabilidad |
|-----|-----------------|
| `core` | Modelo base (UUID + timestamps), utilidades transversales. |
| `accounts` | Usuarios, perfiles, roles, JWT, autenticación. |
| `companies` | Empresas clientes. |
| `services` | Catálogo de servicios de auditoría. |
| `scheduling` | Agenda y calendario (slots de disponibilidad). |
| `audit_requests` | Solicitudes de auditoría y su ciclo de estados. |
| `payments` | Estructura de pagos (sin pasarela real). |
| `dashboard` | Panel administrativo y estadísticas. |

## Puesta en marcha

### Con Docker (recomendado)

```bash
cp .env.example .env          # ajustar valores
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### Local (sin Docker)

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows
pip install -r requirements/development.txt
cp .env.example .env           # ajustar POSTGRES_HOST=localhost
python manage.py migrate
python manage.py runserver
```

## Endpoints útiles

- API: `http://localhost:8000/api/v1/`
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- Admin de Django: `http://localhost:8000/admin/`

## Pruebas

```bash
pytest
```

## Convenciones

- Comunicación y documentación en **español**; código e identificadores en **inglés**.
- Identificadores públicos con **UUID**.
- Lógica de negocio en la capa de **servicios** (`services.py`), vistas finas.
