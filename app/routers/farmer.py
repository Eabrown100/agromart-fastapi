from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database, authentication

router = APIRouter()

@router.post("/products/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(authentication.get_current_active_user)):
    if current_user.role != "farmer":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_product = models.Product(**product.dict(), farmer_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products/", response_model=List[schemas.ProductOut])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db), current_user: models.User = Depends(authentication.get_current_active_user)):
    if current_user.role != "farmer":
        raise HTTPException(status_code=403, detail="Not authorized")
    products = db.query(models.Product).filter(models.Product.farmer_id == current_user.id).offset(skip).limit(limit).all()
    return products

@router.get("/transactions/", response_model=List[schemas.OrderOut])
def read_transactions(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db), current_user: models.User = Depends(authentication.get_current_active_user)):
    if current_user.role != "farmer":
        raise HTTPException(status_code=403, detail="Not authorized")
    products_ids = [product.id for product in current_user.products]
    transactions = db.query(models.Order).filter(models.Order.product_id.in_(products_ids)).offset(skip).limit(limit).all()
    return transactions

@router.get("/produce_left/")
def produce_left(db: Session = Depends(database.get_db), current_user: models.User = Depends(authentication.get_current_active_user)):
    if current_user.role != "farmer":
        raise HTTPException(status_code=403, detail="Not authorized")
    produce_left = db.query(models.Product).filter(models.Product.farmer_id == current_user.id).all()
    total_produce = sum([product.available_quantity for product in produce_left])
    return {"total_produce_left": total_produce}

# Other endpoints can be added here as needed
@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    product: schemas.ProductCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(authentication.get_current_active_user),
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.farmer_id == current_user.id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", response_model=schemas.ProductOut)
def delete_product(
    product_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(authentication.get_current_active_user),
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.farmer_id == current_user.id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return db_product