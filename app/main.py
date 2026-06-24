import logging

from fastapi import FastAPI
from app.routes.ktp_route import router as ktp_router
from app.routes.kk_route import router as kk_router
from app.routes.akta_route import router as akta_router
from app.routes.kp_route import router as kp_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI()

app.include_router(
    ktp_router
)
app.include_router(
    kk_router
)
app.include_router(
    akta_router
)
app.include_router(
    kp_router
)


@app.get("/")
def home():
    return {
        "message": "OCR API"
    }