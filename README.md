# Sistema de Gestión de Transporte Público - API REST

API REST desarrollada con Django REST Framework para la gestión de un sistema de transporte público. tiene gestión de líneas, rutas, paradas, vehículos, choferes, viajes, tarjetas, boletos, mantenimientos e incidentes.

## Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Endpoints de la API](#endpoints-de-la-api)
- [Autenticación](#autenticación)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Documentación Interactiva](#documentación-interactiva)

##  Características

-  **CRUD completo** para 13 entidades del sistema
-  **Autenticación JWT** (JSON Web Tokens)
-  **Sistema de permisos**: usuarios normales y administradores
-  **Filtros y búsquedas** avanzadas
-  **Paginación** automática de resultados
-  **Documentación interactiva** con Swagger/OpenAPI
-  **Validaciones** de datos y manejo de errores
-  **Base de datos PostgreSQL**

## Tecnologías

- **Django 5.0** - Framework web
- **Django REST Framework 3.14** - API REST
- **PostgreSQL** - Base de datos
- **SimpleJWT** - Autenticación JWT
- **drf-spectacular** - Documentación OpenAPI
- **django-filter** - Filtros avanzados
- **django-cors-headers** - CORS para frontend

## Requisitos

- Python 3.10 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)
- virtualenv (recomendado)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd "proyecto seminario_integracion"
```

### 2. Crear y activar entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Configuración

### 1. Configurar PostgreSQL

Crear una base de datos en PostgreSQL:

```sql
CREATE DATABASE transporte_publico;
CREATE USER transporte_user WITH PASSWORD 'tu_password';
ALTER ROLE transporte_user SET client_encoding TO 'utf8';
ALTER ROLE transporte_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE transporte_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE transporte_publico TO transporte_user;
```

### 2. Configurar variables de entorno

Copiar el archivo de ejemplo y editarlo:

```bash
copy .env.example .env
```

Editar `.env` con las credenciales:

```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-muy-segura
DB_NAME=transporte_publico
DB_USER=transporte_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Ejecutar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Crear superusuario

```bash
python manage.py createsuperuser
```

Seguir las instrucciones para crear un usuario administrador.

### 5. Cargar datos de prueba

Crear un archivo `transporte/fixtures/initial_data.json` con datos de ejemplo y cargar:

```bash
python manage.py loaddata initial_data
```

## Ejecución

### Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

### Acceder al panel de administración

URL: `http://localhost:8000/admin`

Usar las credenciales del superusuario creado anteriormente.

## Endpoints de la API

Base URL: `http://localhost:8000/api/`

### Autenticación

| Método | Endpoint | Descripción | Público |
|--------|----------|-------------|---------|
| POST | `/api/token/` | Obtener token JWT | ✅ |
| POST | `/api/token/refresh/` | Refrescar token | ✅ |
| POST | `/api/usuarios/register/` | Registrar usuario | ✅ |

### Entidades Principales (CRUD Completo)

Todas las entidades tienen los siguientes endpoints:

| Método | Endpoint | Descripción | Auth Requerida |
|--------|----------|-------------|----------------|
| GET | `/api/{entidad}/` | Listar todos | No |
| GET | `/api/{entidad}/{id}/` | Obtener detalle | No |
| POST | `/api/{entidad}/` | Crear nuevo | Sí (Admin) |
| PUT | `/api/{entidad}/{id}/` | Actualizar completo | Sí (Admin) |
| PATCH | `/api/{entidad}/{id}/` | Actualizar parcial | Sí (Admin) |
| DELETE | `/api/{entidad}/{id}/` | Eliminar | Sí (Admin) |

#### Listado de Entidades:

1. **lineas** - Líneas de transporte
2. **paradas** - Paradas/estaciones
3. **rutas** - Rutas de las líneas
4. **ruta-paradas** - Relación ruta-parada
5. **vehiculos** - Vehículos/buses
6. **choferes** - Conductores
7. **horarios** - Horarios de rutas
8. **viajes** - Viajes realizados
9. **tarjetas** - Tarjetas de pago
10. **boletos** - Boletos vendidos
11. **mantenimientos** - Mantenimiento de vehículos
12. **incidentes** - Incidentes reportados
13. **usuarios** - Gestión de usuarios

### Endpoints Especiales

#### Tarjetas
```
POST /api/tarjetas/{id}/recargar/
Body: { "monto": 100.50 }
```

#### Vehículos
```
GET /api/vehiculos/{id}/mantenimientos/
```

#### Choferes
```
GET /api/choferes/{id}/viajes/
```

#### Viajes
```
GET /api/viajes/{id}/boletos/
GET /api/viajes/{id}/incidentes/
```

### Filtros y Búsqueda

#### Búsqueda por texto
```
GET /api/lineas/?search=centro
GET /api/paradas/?search=avenida
```

#### Filtros específicos
```
GET /api/lineas/?numero=10
GET /api/viajes/?estado=en_curso
GET /api/viajes/?fecha=2025-11-23
GET /api/tarjetas/?tipo=estudiante&activa=true
```

#### Ordenamiento
```
GET /api/choferes/?ordering=apellido
GET /api/boletos/?ordering=-fecha_compra
```

#### Paginación
```
GET /api/viajes/?page=2
GET /api/boletos/?page_size=20
```

## Autenticación

### 1. Obtener Token JWT

**Request:**
```bash
POST http://localhost:8000/api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "tu_password"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Usar Token en Requests

Incluir el token en el header `Authorization`:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 3. Refrescar Token

**Request:**
```bash
POST http://localhost:8000/api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Ejemplos de Uso

### Ejemplo 1: Listar todas las líneas

```bash
GET http://localhost:8000/api/lineas/
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "numero": 101,
      "nombre": "Centro - Zona Norte",
      "color": "azul",
      "descripcion": "Línea principal",
      "total_rutas": 3
    }
  ]
}
```

### Ejemplo 2: Crear una nueva línea (requiere autenticación)

```bash
POST http://localhost:8000/api/lineas/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "numero": 102,
  "nombre": "Centro - Zona Sur",
  "color": "rojo",
  "descripcion": "Línea secundaria"
}
```

### Ejemplo 3: Crear un viaje

```bash
POST http://localhost:8000/api/viajes/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "ruta": 1,
  "vehiculo": 1,
  "chofer": 1,
  "fecha": "2025-11-23",
  "hora_salida_real": "08:00:00",
  "estado": "en_curso"
}
```

### Ejemplo 4: Comprar un boleto

```bash
POST http://localhost:8000/api/boletos/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "viaje": 1,
  "tarjeta": 1,
  "monto": 50.00,
  "parada_subida": 1
}
```

### Ejemplo 5: Recargar saldo en tarjeta

```bash
POST http://localhost:8000/api/tarjetas/1/recargar/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "monto": 500.00
}
```

### Ejemplo 6: Buscar paradas

```bash
GET http://localhost:8000/api/paradas/?search=Terminal
```

### Ejemplo 7: Filtrar viajes por estado y fecha

```bash
GET http://localhost:8000/api/viajes/?estado=finalizado&fecha=2025-11-23
```

## Documentación

La API incluye documentación interactiva Swagger/OpenAPI:

**Swagger UI:** `http://localhost:8000/api/docs/`

Aquí se puede:
- Ver todos los endpoints disponibles
- Probar los endpoints directamente desde el navegador
- Ver los schemas de datos
- Autenticarte y hacer requests con token

**Schema JSON:** `http://localhost:8000/api/schema/`

## Sistema de Permisos

### Permisos por Endpoint:

| Acción | Usuario Anónimo | Usuario Autenticado | Administrador |
|--------|-----------------|---------------------|---------------|
| GET  | si | si | si |
| POST  | no | no | si |
| PUT/PATCH  | no | no | si |
| DELETE  | no | no | si |

*Excepciones:
- Boletos e Incidentes: usuarios autenticados pueden crear
- Registro de usuarios: público

## Manejo de Errores

La API devuelve códigos de estado HTTP apropiados:

- **200 OK** - Solicitud exitosa
- **201 Created** - Recurso creado exitosamente
- **400 Bad Request** - Datos inválidos
- **401 Unauthorized** - No autenticado
- **403 Forbidden** - Sin permisos
- **404 Not Found** - Recurso no encontrado
- **500 Internal Server Error** - Error del servidor

**Ejemplo de error:**
```json
{
  "numero": ["Este campo es requerido."],
  "nombre": ["Asegúrese de que este campo no tenga más de 100 caracteres."]
}
```

## Estructura del Proyecto

```
proyecto seminario_integracion/
├── transporte_config/          # Configuración principal de Django
│   ├── settings.py            # Configuración del proyecto
│   ├── urls.py                # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── transporte/                 # Aplicación principal
│   ├── models.py              # Modelos de datos
│   ├── serializers.py         # Serializers de DRF
│   ├── views.py               # ViewSets y vistas
│   ├── urls.py                # URLs de la app
│   ├── permissions.py         # Permisos personalizados
│   └── admin.py               # Configuración del admin
├── manage.py                   # Script de gestión de Django
├── requirements.txt            # Dependencias del proyecto
├── .env.example               # Ejemplo de variables de entorno
├── .gitignore                 # Archivos ignorados por git
└── README.md                  # Este archivo
```

## Testing

Para ejecutar las pruebas (si las agrego):

```bash
python manage.py test
```

## Deployment

### para producción:

1. Cambiar `DEBUG = False` en settings.py
2. Configurar `ALLOWED_HOSTS` apropiadamente
3. Usar una clave secreta segura y única
4. Configurar CORS correctamente
5. Usar variables de entorno para credenciales
6. Configurar archivos estáticos con whitenoise o similar
7. Usar un servidor WSGI como Gunicorn
8. Configurar HTTPS

## Autor

Damian Herrera

