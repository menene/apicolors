# API a todo color · 02 Palette API

Segunda etapa funcional del taller. Esta rama recibe una imagen, extrae sus colores dominantes y devuelve una paleta ordenada por frecuencia.

## Incluye

- `POST /api/v1/palettes` con `multipart/form-data`.
- Imágenes JPEG, PNG y WebP de hasta 5 MB.
- Entre 3 y 8 colores solicitados.
- Corrección de orientación EXIF y conversión a RGB.
- Thumbnail máximo de 200 × 200 píxeles.
- Matriz NumPy `N × 3` y agrupamiento con K-means.
- Respuesta tipada con HEX, RGB, porcentaje, dimensiones y tiempo.
- Pruebas del endpoint y del procesamiento.

Los errores todavía utilizan el formato predeterminado de FastAPI. El contrato uniforme, CORS, request IDs y rate limiting se añaden en la siguiente rama.

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

`03-production-hardening` añade errores uniformes, CORS, request IDs y rate limiting.
