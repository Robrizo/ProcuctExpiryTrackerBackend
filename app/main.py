import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import Base, engine
from app.routers import auth, products, user

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Expiry Tracker API",
    description="REST API for household product tracking and 7-day expiry notifications",
    version="1.0.0",
)

cors_origin = os.getenv("CORS_ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(user.router)


@app.get("/health", tags=["health check"])
def health_check():
    return {
        "status": "Ok",
        "service": "Product Expiry Tracker API",
    }