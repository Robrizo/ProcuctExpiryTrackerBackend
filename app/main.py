from fastapi import FastAPI

from config.database import Base, engine
from routers import auth
import models

app = FastAPI(
    title="Product Expiry Tracker API",
    description="REST API for household product tracking and 7-day expiry notifications",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)


# @app.get("/health", tags=["health check"])
# def health_check():
#     return {
#         "status": "Ok",
#         "service": "Product Expiry Tracker API",
#     }