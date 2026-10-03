# API a todo color · 04 Frontend

Cuarta etapa del taller. Esta rama añade una aplicación Vue 3 para consumir el API construido en las ramas anteriores.

## Incluye

- Interfaz creada con Vue 3 y compilada con Vite.
- Selección o drag and drop de imágenes JPEG, PNG y WebP.
- Validación del archivo antes de enviarlo.
- Vista previa de la imagen.
- Selector de 3 a 8 colores.
- Presentación de HEX, RGB y porcentaje.
- Copia de valores HEX al portapapeles.
- Temas claro y oscuro.
- Caddy sirve la SPA y reenvía `/api`, `/docs` y `/openapi.json` al backend.
- Docker Compose inicia el frontend cuando el healthcheck del API está listo.

## Flujo

1. El navegador envía el formulario a `/api/v1/palettes`.
2. Caddy reenvía la petición al servicio `api:8000` usando la red de Docker Compose.
3. FastAPI valida y procesa la imagen.
4. Vue muestra la paleta devuelta por el API.

El navegador no necesita conocer la dirección interna del contenedor del API.

## Variables de entorno

| Variable | Uso |
| --- | --- |
| `APP_PORT` | Puerto público de la aplicación Vue. |
| `API_PORT` | Puerto publicado por Docker Compose. |
| `CORS_ORIGINS` | Orígenes autorizados, separados por comas. |
| `TRUSTED_HOSTS` | Valores permitidos para el encabezado `Host`. |
| `API_RATE_LIMIT` | Límite predeterminado por IP. |
| `PALETTE_RATE_LIMIT` | Límite del procesamiento de paletas por IP. |

## Ejecutar

```bash
cp .env.example .env
docker compose up --build
```

La aplicación queda disponible en `http://127.0.0.1:8086`.

| Recurso | URL |
| --- | --- |
| Aplicación | `http://127.0.0.1:8086` |
| Ping | `http://127.0.0.1:8087/api/v1/ping` |
| Paletas | `http://127.0.0.1:8087/api/v1/palettes` |
| Swagger | `http://127.0.0.1:8087/docs` |
| OpenAPI | `http://127.0.0.1:8087/openapi.json` |

Swagger también está disponible a través de Caddy en `http://127.0.0.1:8086/docs`.

## Probar

```bash
docker compose run --rm -v ./api:/app api pytest
npm --prefix frontend run build
```

La compilación del frontend también se ejecuta durante `docker compose build`.

## Estructura

```text
api/          FastAPI, procesamiento y pruebas
frontend/     Vue 3, Vite y Caddy
docker-compose.yml
```
