# CLAUDE.md

Guía para Claude Code al trabajar en este repositorio (cert-backend).

## Reglas del proyecto

### Idioma

- **Comunicación y documentación → Español.** Toda la comunicación con el usuario, los mensajes, las explicaciones y los textos para documentar el proyecto (README, comentarios de documentación, descripciones, guías) se escriben en español.
- **Código y desarrollo → Inglés.** Todo lo referente al desarrollo se escribe en inglés: nombres de variables, funciones, clases, archivos, carpetas, tablas de base de datos, columnas, ramas de git, mensajes de commit y cualquier identificador técnico.

## Contexto y Alcance

Backend (solo backend) de una aplicación web para una empresa que realiza **Auditorías Internas, Auditorías MINTRA y Auditorías Externas de Certificación ISO**. El frontend (responsabilidad de otro equipo) será una página web donde las empresas solicitan auditorías; este proyecto expone únicamente una **API REST** que el frontend consumirá.

**Objetivo principal:** permitir que una empresa reserve una auditoría desde la web. Flujo: el cliente entra → ve los servicios disponibles → elige el tipo de auditoría → consulta el calendario de fechas disponibles → escoge fecha y hora → completa los datos de su empresa → realiza el pago (solo estructura del módulo, sin pasarela real) → la solicitud queda registrada → el administrador la gestiona desde el panel.

### Stack técnico

- Python 3.x, Django, Django REST Framework (DRF).
- PostgreSQL.
- Autenticación JWT (SimpleJWT).
- Documentación Swagger/OpenAPI (drf-spectacular).
- Docker + docker-compose.
- Variables de entorno y configuración por ambientes (Development / Production).
- UUID como identificadores públicos.
- Arquitectura modular pragmática por capas (ver `docs/architecture.md`), principios SOLID, Git.

### Módulos principales

- **A. Autenticación y Usuarios** (`accounts`) — login, logout, recuperación de contraseña, gestión de usuarios y perfiles, roles y permisos, JWT. Roles: Super Administrador, Administrador, Cliente (Empresa).
- **B. Empresas Clientes** (`companies`) — datos de las empresas que solicitan auditorías. Una empresa puede tener múltiples solicitudes.
- **C. Servicios de Auditoría** (`services`) — catálogo de servicios ofrecidos.
- **D. Agenda y Calendario** (`scheduling`) — disponibilidad mediante slots predefinidos, bloqueo de fechas, consulta de disponibilidad, reprogramación, sin reservas duplicadas (capacidad 1 por slot).
- **E. Solicitudes de Auditoría** (`audit_requests`) — núcleo del sistema; ciclo de estados de cada solicitud.
- **F. Pagos** (`payments`) — solo estructura para futuras integraciones; sin pasarela real.
- **G. Panel Administrativo** (`dashboard`) — administración de toda la plataforma y estadísticas básicas.

### Documentación de referencia

- `docs/scope.md` — alcance completo del proyecto.
- `docs/architecture.md` — arquitectura y estructura de capas.
- `docs/database-schema.md` — esquema de la base de datos.
