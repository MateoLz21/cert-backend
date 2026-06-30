# Alcance del Proyecto — cert-backend

## 1. Descripción general

El proyecto consiste en desarrollar **únicamente el Backend** de una aplicación web para una empresa dedicada a realizar **Auditorías Internas, Auditorías MINTRA y Auditorías Externas de Certificación ISO**.

El frontend (responsabilidad de otro equipo) será una página web donde las empresas podrán solicitar una auditoría. Este proyecto se encarga de toda la lógica del backend usando **Python, Django, Django REST Framework (DRF) y PostgreSQL**, exponiendo una **API REST** que posteriormente consumirá el frontend.

## 2. Objetivo principal

Permitir que una empresa pueda **reservar una auditoría** desde la página web.

### Flujo de reserva

1. El cliente ingresa a la página web.
2. Visualiza los servicios de auditoría disponibles.
3. Selecciona el tipo de auditoría que necesita.
4. Consulta un calendario con las fechas disponibles.
5. Escoge una fecha y una hora para la auditoría.
6. Completa la información de su empresa.
7. Realiza el pago (por el momento solo se implementa la estructura del módulo, sin pasarela de pago real).
8. La solicitud queda registrada en el sistema.
9. El administrador recibe la nueva solicitud desde el panel administrativo para gestionarla.

## 3. Lineamientos de arquitectura

El backend se desarrolla como una **API REST** con **arquitectura modular** mediante aplicaciones independientes de Django. Cada módulo tiene responsabilidades claramente definidas, con separación entre **modelos, serializers, servicios, vistas, permisos, validaciones y rutas**.

Detalle completo en [`architecture.md`](./architecture.md).

Características transversales:

- PostgreSQL como base de datos, preparada para crecer.
- **UUID** como identificadores públicos.
- Variables de entorno.
- Configuración por ambientes (Development y Production).
- Autenticación **JWT**.
- Documentación con **Swagger/OpenAPI**.
- Pruebas unitarias.
- **Docker**.

## 4. Módulos principales

### A. Autenticación y Usuarios (`accounts`)

Administra el acceso al sistema. Debe permitir:

- Inicio de sesión.
- Cierre de sesión.
- Recuperación de contraseña.
- Gestión de usuarios.
- Gestión de perfiles.
- Roles y permisos.
- Autenticación mediante JWT.

Roles iniciales:

- Super Administrador
- Administrador
- Cliente (Empresa)

### B. Empresas Clientes (`companies`)

Registra la información de las empresas que solicitan auditorías. Cada empresa tendrá:

- Razón social
- RUC
- Dirección
- Representante legal
- Persona de contacto
- Correo
- Teléfono
- Rubro
- Número de trabajadores

Cada empresa podrá tener **múltiples** solicitudes de auditoría.

### C. Servicios de Auditoría (`services`)

Administra los servicios ofrecidos por la empresa. Ejemplos:

- Auditoría Interna
- Auditoría MINTRA
- Auditoría Externa ISO 9001
- Auditoría ISO 14001
- Auditoría ISO 45001

Cada servicio almacena:

- Nombre
- Descripción
- Precio
- Duración estimada
- Estado (Activo/Inactivo)

### D. Agenda y Calendario (`scheduling`)

Uno de los módulos principales. Administra la disponibilidad para realizar auditorías. Debe permitir:

- Registrar fechas disponibles.
- Registrar horarios disponibles.
- Bloquear fechas ocupadas.
- Consultar disponibilidad.
- Reprogramar reservas.
- Evitar reservas duplicadas.

**Modelo elegido:** slots de disponibilidad predefinidos (`AvailabilitySlot`) con **capacidad 1** (una auditoría a la vez por horario). El administrador crea los slots disponibles; cuando un cliente selecciona un slot disponible, el sistema lo reserva automáticamente y lo marca como ocupado, impidiendo reservas duplicadas.

### E. Solicitudes de Auditoría (`audit_requests`)

Núcleo del sistema. Cada solicitud almacena:

- Código único
- Empresa
- Servicio solicitado
- Fecha elegida
- Hora
- Estado
- Fecha de creación
- Observaciones

Estados iniciales:

- Pendiente de pago
- Pagada
- Confirmada
- Programada
- Finalizada
- Cancelada

### F. Pagos (`payments`)

Por el momento solo queda **preparado para futuras integraciones**. Debe registrar:

- Solicitud asociada
- Monto
- Método de pago
- Estado del pago
- Fecha

**No se implementa ninguna pasarela de pago real**, únicamente la estructura de la base de datos y los endpoints necesarios para futuras integraciones.

### G. Panel Administrativo (`dashboard`)

Administra toda la plataforma. Debe incluir:

- Dashboard.
- Gestión de usuarios.
- Gestión de empresas.
- Gestión de servicios.
- Gestión de solicitudes.
- Gestión del calendario.
- Gestión de pagos.
- Estadísticas básicas.

## 5. Requisitos técnicos

- Python 3.x
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Swagger/OpenAPI
- Docker
- Variables de entorno
- UUID
- Arquitectura Modular
- Clean Architecture (aplicada de forma pragmática por capas)
- Principios SOLID
- Git

## 6. Fuera de alcance

- Desarrollo del frontend (otra responsabilidad).
- Integración con una pasarela de pago real (solo se prepara la estructura).
- Cualquier funcionalidad no descrita en los módulos A–G.
