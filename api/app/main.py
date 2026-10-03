from fastapi import FastAPI


app = FastAPI(
    title="API a todo color",
    description="Extrae los colores predominantes de una imagen.",
    version="1.0.0",
)
