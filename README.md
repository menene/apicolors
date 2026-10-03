# API a todo color · 03 Production Hardening

Tercera etapa funcional del taller. Esta rama conserva el API de paletas y añade controles para exponerlo de forma pública.

## Incluye

- Contrato uniforme para errores HTTP, validación y rate limiting.
- `X-Request-ID` generado por el API o conservado cuando el cliente envía uno válido.
- CORS restringido a los orígenes configurados.
- Validación del encabezado `Host`.
- Rate limiting por dirección IP.
- Límite general de `10/second` aplicado a las rutas regulares del API.
- Límite específico de `2/second` para `POST /api/v1/palettes`.
- Respuestas `429 Too Many Requests` con `Retry-After`.

El endpoint de paletas tiene un límite menor porque decodificar imágenes y ejecutar K-means consume más CPU que responder al ping.

## Contrato de errores

Todos los errores producidos por el API utilizan la misma estructura:

```json
{
  "error": {
    "code": "unsupported_media_type",
    "message": "Formato no permitido. Utiliza JPEG, PNG o WebP.",
    "request_id": "workshop-request-01"
  }
}
```

`code` permite que el cliente identifique el error sin interpretar el mensaje. `request_id` relaciona la respuesta con los logs del servidor.

## Variables de entorno

| Variable | Uso |
| --- | --- |
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

La API queda disponible en `http://127.0.0.1:8087`.

| Recurso | URL |
| --- | --- |
| Ping | `http://127.0.0.1:8087/api/v1/ping` |
| Paletas | `http://127.0.0.1:8087/api/v1/palettes` |
| Swagger | `http://127.0.0.1:8087/docs` |
| OpenAPI | `http://127.0.0.1:8087/openapi.json` |

## Probar

```bash
docker compose run --rm -v ./api:/app api pytest
```

## Siguiente rama

`04-vue-integration` añade la interfaz Vue 3 y la conecta con el API.
