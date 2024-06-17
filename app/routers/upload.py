from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
import uuid
from .. import models, database, authentication

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    dependencies=[Depends(authentication.get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

UPLOAD_DIRECTORY = "./uploads"

@router.post("/product/{product_id}/image", response_model=dict)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(authentication.get_current_active_user),
):
    product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.farmer_id == current_user.id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found or not owned by user")

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    product.image_url = file_path
    db.commit()
    db.refresh(product)

    return {"image_url": product.image_url}

@router.post("/user/profile-picture", response_model=dict)
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(authentication.get_current_active_user),
):
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.profile_picture = file_path
    db.commit()
    db.refresh(current_user)

    return {"profile_picture": current_user.profile_picture}
