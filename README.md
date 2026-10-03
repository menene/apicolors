# API a todo color · 01 API Foundation

Primera etapa funcional del taller. Esta rama define la estructura versionada de la API y añade un endpoint para comprobar su disponibilidad.

## Incluye

- Aplicación creada mediante una factory.
- Routers separados bajo `/api/v1`.
- `GET /api/v1/ping` con respuesta tipada.
- Swagger en `/docs` y esquema OpenAPI en `/openapi.json`.
- Healthcheck del contenedor basado en el endpoint de ping.
- Pruebas del endpoint y del versionado.

Todavía no incluye carga de imágenes, K-means, seguridad ni frontend.

## Ejecutar

```bash
cp .env.example .env
docker compose up --build
```

La API queda disponible en `http://127.0.0.1:8087`.

| Recurso | URL |
| --- | --- |
| Ping | `http://127.0.0.1:8087/api/v1/ping` |
| Swagger | `http://127.0.0.1:8087/docs` |
| OpenAPI | `http://127.0.0.1:8087/openapi.json` |

## Probar

```bash
docker compose run --rm -v ./api:/app api pytest
```

## Siguiente rama

`02-palette-api` añade el upload de imágenes, el procesamiento RGB y K-means.
