# Arquitectura — cert-backend

## 1. Enfoque

API REST construida con **Django + Django REST Framework**, organizada como una **arquitectura modular pragmática por capas**. No se aplica Clean Architecture estricta (sin entidades de dominio puras desacopladas del ORM); en su lugar se separa la lógica de negocio de las vistas y del acceso a datos mediante una **capa de servicios**, manteniendo simplicidad y compatibilidad natural con DRF.

Principios:

- **SOLID** y responsabilidad única por módulo y por archivo.
- Vistas finas: las vistas orquestan, los **servicios** contienen la lógica de negocio.
- Cada app es un módulo independiente con interfaz clara (serializers + urls).
- **UUID** como identificador público (PK) en todos los modelos de dominio.

## 2. Estructura de capas (por app)

Cada aplicación Django sigue el mismo patrón de capas:

```
<app>/
├── models.py          # Modelos ORM (persistencia)
├── repositories.py    # Acceso a datos / consultas reutilizables (opcional por app)
├── services.py        # Lógica de negocio, casos de uso, transacciones
├── serializers.py     # Validación y (de)serialización DRF (interfaz de entrada/salida)
├── views.py           # ViewSets / APIViews (orquestación HTTP, delgadas)
├── permissions.py     # Permisos y reglas de acceso por rol
├── urls.py            # Rutas de la app
├── admin.py           # Registro en Django admin
├── apps.py
├── migrations/
└── tests/             # Pruebas unitarias y de integración de la app
    ├── test_models.py
    ├── test_services.py
    └── test_views.py
```

### Responsabilidad de cada capa

| Capa | Responsabilidad | No debe |
|------|-----------------|---------|
| `models` | Definir tablas, relaciones, constraints, choices. | Contener reglas de negocio complejas. |
| `repositories` | Encapsular consultas al ORM reutilizables/complejas. | Llamar a servicios. |
| `services` | Reglas de negocio, validaciones de negocio, transacciones, coordinación entre modelos. | Conocer detalles de HTTP/request. |
| `serializers` | Validar entrada, transformar salida. | Contener lógica de negocio. |
| `views` | Recibir request, llamar al servicio, devolver response. | Contener lógica de negocio ni queries complejas. |
| `permissions` | Autorización por rol/objeto. | — |

Flujo de una petición:

```
Request → urls → view → serializer (validación) → service (lógica) → repository/model (datos) → service → serializer (salida) → Response
```

## 3. Módulos (apps Django)

| App | Módulo | Responsabilidad |
|-----|--------|-----------------|
| `core` | Transversal | BaseModel (UUID + timestamps), mixins, utilidades, paginación, manejo de errores, permisos base. |
| `accounts` | A | Usuarios, perfiles, roles/permisos, JWT, login/logout, recuperación de contraseña. |
| `companies` | B | Empresas clientes y sus datos. |
| `services` | C | Catálogo de servicios de auditoría. |
| `scheduling` | D | Agenda: slots de disponibilidad, bloqueo, consulta, reserva, reprogramación. |
| `audit_requests` | E | Solicitudes de auditoría y su ciclo de estados. |
| `payments` | F | Estructura de pagos (sin pasarela real). |
| `dashboard` | G | Panel administrativo y estadísticas básicas (agrega datos de otras apps). |

`dashboard` no define modelos de dominio propios; consume servicios/consultas de las demás apps para exponer agregados y estadísticas.

## 4. Estructura del proyecto

```
cert-backend/
├── config/                     # Proyecto Django
│   ├── settings/
│   │   ├── base.py             # Configuración común
│   │   ├── development.py      # Ambiente Development
│   │   └── production.py       # Ambiente Production
│   ├── urls.py                 # Enrutado raíz + Swagger
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/
│   ├── accounts/
│   ├── companies/
│   ├── services/
│   ├── scheduling/
│   ├── audit_requests/
│   ├── payments/
│   └── dashboard/
├── docs/
│   ├── scope.md
│   ├── architecture.md
│   └── database-schema.md
├── .env.example
├── .env                        # No versionado
├── requirements/               # base.txt / development.txt / production.txt
├── manage.py
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 5. Decisiones transversales

### Configuración por ambientes
`config/settings/` dividido en `base`, `development`, `production`. La variable de entorno `DJANGO_SETTINGS_MODULE` selecciona el ambiente. Toda credencial/secreto vive en variables de entorno (`.env`, leído con `django-environ` o similar); `.env.example` documenta las variables sin valores reales.

### Identificadores
Todos los modelos de dominio heredan de `core.BaseModel` con PK `id = UUIDField(primary_key=True, default=uuid4, editable=False)` + `created_at` / `updated_at`.

### Autenticación y autorización
- **JWT** vía `djangorestframework-simplejwt` (access + refresh).
- Roles en `accounts`: `super_admin`, `admin`, `client`.
- Permisos personalizados en `permissions.py` por app; los endpoints del panel exigen rol admin/super_admin.

### Documentación de la API
**Swagger/OpenAPI** con `drf-spectacular`, expuesto en `/api/schema/`, `/api/docs/` (Swagger UI) y `/api/redoc/`.

### Versionado de la API
Prefijo `/api/v1/` para permitir evolución futura.

### Pruebas
Pruebas unitarias por capa (modelos, servicios) e integración (vistas) en `tests/` de cada app. `pytest` + `pytest-django` (o `unittest` de Django).

### Contenedores
`Dockerfile` para la imagen de la app y `docker-compose.yml` con servicios `web` (Django) y `db` (PostgreSQL); preparado para añadir servicios futuros (p. ej. cache, worker).

## 6. Reglas de negocio clave

- **Reserva sin duplicados:** un `AvailabilitySlot` tiene capacidad 1. La reserva se realiza dentro de una transacción con bloqueo (`select_for_update`) para evitar condiciones de carrera; al reservar, el slot pasa a estado `booked` y queda asociado a una única `AuditRequest` (relación 1:1).
- **Ciclo de estados de la solicitud:** las transiciones de estado de `AuditRequest` se controlan en `audit_requests/services.py` (no se cambian estados arbitrariamente desde la vista).
- **Reprogramación:** liberar el slot anterior (`available`) y reservar el nuevo dentro de la misma transacción.
