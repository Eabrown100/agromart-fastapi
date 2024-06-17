from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database

router = APIRouter()

@router.get("/sales", response_model=List[schemas.OrderOut])
def get_sales(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    sales = db.query(models.Order).offset(skip).limit(limit).all()
    return sales

@router.get("/top_products", response_model=List[schemas.ProductOut])
def get_top_products(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    top_products = db.query(models.Product).order_by(models.Product.price.desc()).offset(skip).limit(limit).all()
    return top_products
