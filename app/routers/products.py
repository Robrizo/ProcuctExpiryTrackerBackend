from datetime import date, datetime
from typing import List
import uuid

from fastapi import APIRouter, HTTPException
from starlette import status

from app.auth.jwt import user_dependancy
from app.config.database import db_dependency
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.tasks.expiry_checker import calculate_status

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

def serialize_product(product: Product) -> dict:
    status, days_until_expiry = calculate_status(product.expiry_date)
    return {
        "id": product.id,
        "user_id": product.user_id,
        "name": product.name,
        "category": product.category,
        "quantity": product.quantity,
        "purchase_date": product.purchase_date,
        "expiry_date": product.expiry_date,
        "notes": product.notes,
        "reminder_sent": product.reminder_sent,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "status": status,
        "days_until_expiry": days_until_expiry
    }

@router.get("", response_model=List[ProductResponse])
def get_products(user: user_dependancy, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication, you cannot access products")
    products = db.query(Product).filter(Product.user_id == user["user_id"]).all()
    return [serialize_product(product) for product in products]

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: uuid.UUID, user: user_dependancy, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication, you cannot access this product")
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user["user_id"]).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return serialize_product(product)

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(user: user_dependancy, db: db_dependency, product: ProductCreate):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="failed authentication, you cannot create a product")

    if product.purchase_date > product.expiry_date:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Expiry date cannot be earlier than purchase date.")
    
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

    return serialize_product(new_product)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: uuid.UUID, user: user_dependancy, db: db_dependency, product: ProductUpdate):
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="failed authentication, you cannot update this product")
    existing_product = db.query(Product).filter(Product.id == product_id, Product.user_id == user["user_id"]).first()
    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    update_data = product.model_dump(exclude_unset=True)

    new_purchase = update_data.get("purchase_date")
    new_expiry = update_data.get("expiry_date")
    if new_purchase and new_expiry and new_purchase > new_expiry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Purchase date cannot be after expiry date")

    # reset reminder_sent to False if expiry_date is updated
    if "expiry_date" in update_data and update_data["expiry_date"] != existing_product.expiry_date:
        today = date.today()
        if update_data["expiry_date"] > today:
            existing_product.reminder_sent = False

    for key, value in update_data.items():
        setattr(existing_product, key, value)

    existing_product.updated_at = datetime.now()

    db.commit()
    db.refresh(existing_product)

    return serialize_product(existing_product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: uuid.UUID, user: user_dependancy, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="failed authentication, you cannot delete this product")
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user["user_id"]).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()