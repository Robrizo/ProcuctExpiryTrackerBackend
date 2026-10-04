from fastapi import APIRouter, HTTPException
from starlette import status

from app.auth.jwt import user_dependancy
from app.config.database import db_dependency, get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get("")
def get_products(user: user_dependancy, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication")
    return db.query(Product).all()

@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(user: user_dependancy, db: db_dependency, product: ProductCreate):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication")
    new_product = Product(
        user_id=user["user_id"],
        name=product.name,
        category=product.category,
        quantity=product.quantity,
        purchase_date=product.purchase_date,
        expiry_date=product.expiry_date,
        notes=product.notes,
        reminder_sent=False
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product