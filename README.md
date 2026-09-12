# Security Exercise – Secret Injection, Encryption and Rotation

El objetivo es demostrar cómo se puede **inyectar secretos desde variables de entorno**, **integrar cifrado/descifrado de datos** (AES‑256‑GCM) en una API, y **rotar automáticamente el secreto de autenticación cada 2 minutos** sin afectar la disponibilidad del frontend ni la capacidad de leer datos existentes en la base de datos.



## Estructura del proyecto

```
security-exercise/

├── docker-compose.yml

├── security-api/                     # Backend (Flask)

│   ├── Dockerfile

│   ├── app.py

│   ├── config.py

│   ├── crypto_service.py

│   ├── rotate_secret.py

│   └── requirements.txt

└── security-frontend/                # Frontend + NGINX

    ├── Dockerfile

    ├── entrypoint.sh

    ├── nginx.conf

    └── html/

        ├── index.html

        ├── styles.css

        └── app.js
```

# Arquitectura final

```
[ Usuario / Navegador (Windows) ]

        │

        ▼

http://localhost:8080 (Mapeo: 8080 -> 80)

        │

┌───────┴───────────────────────────────┐

│  Contenedor Frontend (security-frontend) │

│  - NGINX (Puerto 80)                    │

│  - Archivos estáticos (index.html, CSS) │

│  - app.js (con API_KEY inyectado)       │

└───────┬───────────────────────────────┘

        │

┌───────┴───────────────────────────────┐  (Volumen compartido)

│  carpeta html/ (en máquina host)      │  (sincroniza app.js)

└───────┬───────────────────────────────┘

        │ (proxy: /health, /api/*)

        ▼

┌─────────────────────────────────────────────────────────────┐

│  Contenedor Backend (security-backend)                     │

│  ┌───────────────────────────────────────────────────────┐ │

│  │  Variables de Entorno                               │ │

│  │  - API_SECRET=my-secret... (inicial)               │ │

│  │  - DB_ENCRYPTION_KEY=3Lowej... (fija)              │ │

│  └───────────────────────────────────────────────────────┘ │

│  ┌───────────────────────────────────────────────────────┐ │

│  │  Proceso Flask (app.py, Puerto 3000)                │ │

│  │  - Endpoints: /health, /api/data, /api/secrets      │ │

│  │  - validate_api_key() lee de /app/.secret           │ │

│  └───────────────────────────────────────────────────────┘ │

│  ┌───────────────────────────────────────────────────────┐ │

│  │  Servicio de Cifrado (crypto_service.py - AES-256)  │ │

│  │  Usa DB_ENCRYPTION_KEY                              │ │

│  └───────────────────────────────────────────────────────┘ │

│  ┌───────────────────────────────────────────────────────┐ │

│  │  Script Rotador (rotate_secret.py)                  │ │

│  │  - Ejecuta cada 2 minutos                           │ │

│  │  - Genera nuevo API_SECRET                          │ │

│  │  - Escribe en /app/.secret                          │ │

│  │  - Escribe en /shared-html/app.js (volumen)        │ │

│  └───────────────────────────────────────────────────────┘ │

└──────────────────────┬────────────────────────────────────┘

                       │

                       ▼

              [ Base de datos SQLite ]

              (bank.db - Tabla 'secrets')

              Columnas: name, value_encrypted

              (Datos cifrados con DB_ENCRYPTION_KEY)
```

---

## Tecnologías utilizadas

| Componente       | Tecnología / Herramienta                  |

|------------------|-------------------------------------------|

| Backend API      | Python 3.11 + Flask                       |

| Cifrado          | AES‑256‑GCM (cryptography)                |

| Base de datos    | SQLite                                    |

| Proxy inverso    | NGINX                                     |

| Frontend         | HTML5, CSS3, JavaScript (Fetch API)       |

| Contenedorización| Docker + Docker Compose                   |

| Rotación         | Script Python en segundo plano            |

--- 

## Instalación y ejecución

### Requisitos previos

- [Docker]([https://www.docker.com/](https://www.docker.com/)) y [Docker Compose]([https://docs.docker.com/compose/](https://docs.docker.com/compose/)) instalados.

- (Opcional) [Git]([https://git-scm.com/](https://git-scm.com/)) para clonar el repositorio.

### 1. Clonar el repositorio

git clone [https://github.com/tu-usuario/security-exercise.git](https://github.com/tu-usuario/security-exercise.git)

```
cd security-exercise
```

### 2. Configurar variables de entorno (opcional)

El archivo `docker-compose.yml` ya contiene valores de ejemplo. Puedes modificarlos si lo deseas.

### 3. Construir y levantar los contenedores

```
docker-compose down -v

docker-compose build --no-cache

docker-compose up -d
```

### 4. Verificar que todo está funcionando

- Accede al frontend: [[http://localhost:8080](http://localhost:8080)](http://localhost:8080](http://localhost:8080))

- Comprueba el estado del backend:

  curl.exe [http://localhost:8080/health](http://localhost:8080/health)

  Debería responder `{"status":"ok"}`.



## Cómo funciona

### 1. Inyección de secretos desde variables de entorno

- *`API_SECRET`**: Se inyecta en el contenedor `backend` y `frontend` desde `docker-compose.yml`.

- *`DB_ENCRYPTION_KEY`**: Solo en el backend, es fija y **no se rota**.

### 2. Autenticación

- El frontend incluye en cada petición el header `x-api-key` con el valor actual de `API_SECRET`.

- El backend valida este header contra el valor almacenado en `/app/.secret` (o con fallback a la variable de entorno).

### 3. Cifrado / Descifrado (AES‑256‑GCM)

- *`crypto_service.py`** implementa el cifrado y descifrado usando la clave `DB_ENCRYPTION_KEY`.

- Los endpoints `/api/secrets` permiten:

  - `POST`: cifra y guarda un secreto en SQLite.

  - `GET /<id>`: recupera y descifra el secreto.

### 4. Rotación automática del `API_SECRET` (cada 2 minutos)

- El script `rotate_secret.py` se ejecuta en segundo plano dentro del contenedor `backend`.

- Genera un nuevo valor aleatorio (32 bytes en Base64) y lo escribe en:

  - `/app/.secret` (para que Flask lo lea en la próxima petición).

  - `/shared-html/app.js` (para actualizar el frontend, gracias al volumen compartido).

- La rotación no afecta a `DB_ENCRYPTION_KEY`.

### 5. Frontend adaptativo

- El archivo `app.js` contiene `const API_KEY = "{{API_SECRET}}";` que es reemplazado por el valor actual al iniciar el contenedor mediante `entrypoint.sh`.

- Cuando el rotador actualiza `app.js`, el frontend lo refleja tras recargar la página (F5).

## Comandos útiles

| Acción | Comando |

|--------|---------|

| Levantar contenedores | `docker-compose up -d` |

| Detener contenedores | `docker-compose down` |

| Ver logs del backend | `docker logs security-backend -f` |

| Ver logs del frontend | `docker logs security-frontend -f` |

| Obtener valor actual de `API_SECRET` | `docker exec -it security-backend printenv API_SECRET` |

| Ver contenido cifrado en BD | `docker exec -it security-backend sqlite3 bank.db "SELECT * FROM secrets;"` |

---

