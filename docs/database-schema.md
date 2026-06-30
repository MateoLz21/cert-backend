# Esquema de Base de Datos — cert-backend

Motor: **PostgreSQL**. Todos los identificadores públicos son **UUID**. Todas las tablas de dominio incluyen `id (UUID, PK)`, `created_at` y `updated_at` (heredados de `core.BaseModel`).

> Convención: nombres de tablas, columnas y enums en **inglés**. Los textos descriptivos en español.

## 1. Diagrama de relaciones (resumen)

```
User 1───1 Profile
User 1───* Company            (un usuario cliente puede gestionar una o varias empresas)
Company 1───* AuditRequest
Service 1───* AuditRequest
AvailabilitySlot 1───1 AuditRequest   (slot reservado ↔ una solicitud)
AuditRequest 1───* Payment
```

## 2. Módulo A — Autenticación y Usuarios (`accounts`)

### `users`
Usuario del sistema. Extiende el modelo de usuario de Django (`AbstractBaseUser` / `AbstractUser`), con `email` como identificador de login.

| Columna | Tipo | Notas |
|---------|------|-------|
| id | UUID | PK |
| email | varchar | Único, usado para login |
| password | varchar | Hash |
| first_name | varchar | |
| last_name | varchar | |
| role | varchar (enum `UserRole`) | `super_admin`, `admin`, `client` |
| is_active | boolean | default `true` |
| is_staff | boolean | acceso al admin de Django |
| last_login | timestamp | |
| created_at / updated_at | timestamp | |

**Enum `UserRole`:** `super_admin`, `admin`, `client`.

### `profiles`
Información adicional del usuario.

| Columna | Tipo | Notas |
|---------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users (1:1, on_delete CASCADE) |
| phone | varchar | nullable |
| avatar | varchar | URL/ruta, nullable |
| document_id | varchar | DNI/identificación, nullable |
| created_at / updated_at | timestamp | |

### Recuperación de contraseña
Se usa el mecanismo de tokens de Django / SimpleJWT. Si se requiere persistencia propia, tabla opcional `password_reset_tokens` (user_id, token, expires_at, used). No obligatoria en la primera versión.

## 3. Módulo B — Empresas Clientes (`companies`)

### `companies`

| Columna | Tipo | Notas |
|---------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users (propietario/gestor, on_delete PROTECT), nullable |
| business_name | varchar | Razón social |
| ruc | varchar(11) | Único |
| address | varchar | Dirección |
| legal_representative | varchar | Representante legal |
| contact_person | varchar | Persona de contacto |
| email | varchar | Correo |
| phone | varchar | Teléfono |
| business_sector | varchar | Rubro |
| employee_count | integer | Número de trabajadores |
| created_at / updated_at | timestamp | |

Relación: una empresa puede tener **múltiples** `audit_requests`.

## 4. Módulo C — Servicios de Auditoría (`services`)

### `services`

| Columna | Tipo | Notas |
|---------|------|-------|
| id | UUID | PK |
| name | varchar | Nombre (ej. "Auditoría ISO 9001") |
| description | text | Descripción |
| price | decimal(10,2) | Precio |
| estimated_duration | interval / integer (min) | Duración estimada |
| is_active | boolean | Estado Activo/Inactivo, default `true` |
| created_at / updated_at | timestamp | |

## 5. Módulo D — Agenda y Calendario (`scheduling`)

### `availability_slots`
Franja horaria disponible creada por el administrador. Capacidad 1.

| Columna | Tipo | Notas |
|---------|------|-------|
| id | UUID | PK |
| date | date | Fecha del slot |
| start_time | time | Hora de inicio |
| end_time | time | Hora de fin |
| status | varchar (enum `SlotStatus`) | `available`, `blocked`, `booked` |
| created_at / updated_at | timestamp | |

**Enum `SlotStatus`:** `available`, `blocked`, `booked`.

Restricciones:

- `UNIQUE (date, start_time, end_time)` para evitar slots duplicados.
- Validación: `end_time > start_time`.
- Un slot en estado `booked` está asociado a exactamente una `audit_request` (ver relación 1:1).
- La reserva se hace con `select_for_update` dentro de una transacción para evitar dobles reservas.

## 6. Módulo E — Solicitudes de Auditoría (`audit_requests`)

### `audit_requests`
Núcleo del sistema.

| Columna | Tipo | Notas |
|---------|------|-------|
| id | UUID | PK |
| code | varchar | Código único legible (ej. `AUD-2026-0001`), único |
| company_id | UUID | FK → companies (on_delete PROTECT) |
| service_id | UUID | FK → services (on_delete PROTECT) |
| slot_id | UUID | FK → availability_slots (1:1, on_delete PROTECT), nullable hasta reservar |
| status | varchar (enum `AuditRequestStatus`) | ver enum |
| notes | text | Observaciones, nullable |
| created_at / updated_at | timestamp | `created_at` = fecha de creación |

`date` y `time` de la auditoría se derivan del `slot` asociado (no se duplican; se exponen vía serializer).

**Enum `AuditRequestStatus`:**

| Valor | Descripción |
|-------|-------------|
| `pending_payment` | Pendiente de pago |
| `paid` | Pagada |
| `confirmed` | Confirmada |
| `scheduled` | Programada |
| `finished` | Finalizada |
| `cancelled` | Cancelada |

Relación 1:1 con `availability_slots`: `slot_id` con constraint `UNIQUE` → un slot no puede pertenecer a dos solicitudes.

## 7. Módulo F — Pagos (`payments`)

> Solo estructura. Sin pasarela de pago real.

### `payments`

| Columna | Tipo | Notas |
|---------|------|-------|
| id | UUID | PK |
| audit_request_id | UUID | FK → audit_requests (on_delete PROTECT) |
| amount | decimal(10,2) | Monto |
| payment_method | varchar (enum `PaymentMethod`) | Método de pago |
| status | varchar (enum `PaymentStatus`) | Estado del pago |
| paid_at | timestamp | Fecha de pago, nullable |
| created_at / updated_at | timestamp | |

**Enum `PaymentMethod`:** `card`, `bank_transfer`, `cash`, `other` (extensible).

**Enum `PaymentStatus`:** `pending`, `completed`, `failed`, `refunded`.

## 8. Módulo G — Panel Administrativo (`dashboard`)

No define tablas propias. Lee y agrega datos de las demás tablas para exponer estadísticas (conteos por estado de solicitud, ingresos registrados, ocupación del calendario, etc.).

## 9. Índices y constraints recomendados

| Tabla | Índice / Constraint |
|-------|---------------------|
| users | `UNIQUE(email)` |
| companies | `UNIQUE(ruc)` |
| availability_slots | `UNIQUE(date, start_time, end_time)`, índice en `(date, status)` |
| audit_requests | `UNIQUE(code)`, `UNIQUE(slot_id)`, índice en `status`, índice en `company_id` |
| payments | índice en `audit_request_id`, índice en `status` |

## 10. Notas de integridad

- Borrados: usar `PROTECT` en FKs hacia datos históricos (empresas, servicios, solicitudes, pagos) para no perder trazabilidad; `CASCADE` solo en relaciones 1:1 dependientes (perfil ↔ usuario).
- Las transiciones de `AuditRequestStatus` y la liberación/reserva de slots se gestionan en la capa de servicios, no directamente desde la base de datos.
