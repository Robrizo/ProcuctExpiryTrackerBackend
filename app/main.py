from app.config.database import Base, engine
from fastapi import FastAPI
from app.routers import auth, products

app = FastAPI(
    title="Product Expiry Tracker API",
    description="REST API for household product tracking and 7-day expiry notifications",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(products.router)


# @app.get("/health", tags=["health check"])
# def health_check():
#     return {
#         "status": "Ok",
#         "service": "Product Expiry Tracker API",
#     }