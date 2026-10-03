# API a todo color · 00 Starter

Punto de partida del taller. Esta rama contiene una aplicación FastAPI mínima y la infraestructura necesaria para ejecutarla con Docker.

## Incluye

- Python 3.13 y FastAPI.
- Un contenedor para la API.
- El puerto local configurable mediante `.env`.
- Una prueba que confirma que OpenAPI está disponible.

Todavía no incluye rutas de negocio, procesamiento de imágenes, seguridad ni frontend.

## Ejecutar

```bash
cp .env.example .env
docker compose up --build
```

La API queda disponible en `http://127.0.0.1:8087` y la documentación inicial en `http://127.0.0.1:8087/docs`.

## Probar

```bash
docker compose run --rm -v ./api:/app api pytest
```

## Siguiente rama

`01-api-foundation` añade el router versionado y `GET /api/v1/ping`.
