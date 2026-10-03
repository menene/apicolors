from fastapi import FastAPI

from app.api.router import api_router


def create_application() -> FastAPI:
    application = FastAPI(
        title="API a todo color",
        description="Extrae los colores predominantes de una imagen.",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    application.include_router(api_router)
    return application


app = create_application()
