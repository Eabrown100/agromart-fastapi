from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str

class UserOut(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    role: str
    profile_picture: Optional[str]  # New field for profile picture
    

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    available_quantity: int

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    farmer_id: int

    class Config:
        from_attributes = True
class Product(ProductBase):
    id: int
    image_url: Optional[str]  # New field for produce image
    owner_id: int

class OrderBase(BaseModel):
    product_id: int
    quantity: int
    timestamp: Optional[datetime] = None

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    buyer_id: int
    total_price: float
    timestamp: datetime

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    product_id: int
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class CreatePaymentIntentRequest(BaseModel):
    amount: int
    currency: str
    payment_method: str

class MobileMoneyPaymentRequest(BaseModel):
    amount: int
    phone_number: str
    currency: str
    provider: str
