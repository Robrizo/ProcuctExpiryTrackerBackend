from fastapi import APIRouter, HTTPException
from app.config.database import db_dependency, get_db
from app.auth.jwt import user_dependancy
from starlette import status
from app.models.product import Product

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get("")
def get_products(user: user_dependancy, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication")
    return db.query(Product).all()