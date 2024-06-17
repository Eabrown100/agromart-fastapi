from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas, database, authentication

router = APIRouter()

@router.get("/products/", response_model=List[schemas.ProductOut])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.post("/orders/", response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(authentication.get_current_active_user)):
    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.available_quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough product available")
    total_price = order.quantity * product.price
    db_order = models.Order(**order.dict(exclude={"timestamp"}), buyer_id=current_user.id, total_price=total_price,timestamp=order.timestamp or datetime.utcnow())
    product.available_quantity -= order.quantity
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/orders/", response_model=List[schemas.OrderOut])
def read_orders(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db), current_user: models.User = Depends(authentication.get_current_active_user)):
    if current_user.role != "buyer":
        raise HTTPException(status_code=403, detail="Not authorized")
    orders = db.query(models.Order).filter(models.Order.buyer_id == current_user.id).offset(skip).limit(limit).all()
    return orders

@router.post("/reviews/", response_model=schemas.ReviewOut)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(authentication.get_current_active_user)):
    product = db.query(models.Product).filter(models.Product.id == review.product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db_review = models.Review(**review.dict(), user_id=current_user.id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.get("/reviews/{product_id}", response_model=List[schemas.ReviewOut])
def read_reviews(product_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    reviews = db.query(models.Review).filter(models.Review.product_id == product_id).offset(skip).limit(limit).all()
    return reviews

# Other endpoints can be added here as needed
@router.put("/orders/{order_id}", response_model=schemas.OrderOut)
def update_order(
    order_id: int,
    order: schemas.OrderCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(authentication.get_current_active_user),
):
    db_order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.buyer_id == current_user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    for key, value in order.dict().items():
        setattr(db_order, key, value)
    db_order.total_price = order.quantity * db.query(models.Product).filter(models.Product.id == order.product_id).first().price
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/orders/{order_id}", response_model=schemas.OrderOut)
def delete_order(
    order_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(authentication.get_current_active_user),
):
    db_order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.buyer_id == current_user.id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return db_order