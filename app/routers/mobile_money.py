from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests
import os
from .. import schemas, models, database, authentication

router = APIRouter(
    prefix="/mobile-money",
    tags=["mobile-money"],
    dependencies=[Depends(authentication.get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

API_KEY = os.getenv("MOBILE_MONEY_API_KEY")
API_SECRET = os.getenv("MOBILE_MONEY_API_SECRET")
CALLBACK_URL = os.getenv("MOBILE_MONEY_CALLBACK_URL")

@router.post("/initiate-payment", response_model=dict)
def initiate_mobile_money_payment(
    payment_request: schemas.MobileMoneyPaymentRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(authentication.get_current_active_user),
):
    try:
        response = requests.post(
            "https://api.mobilemoneyprovider.com/v1/payments",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "amount": payment_request.amount,
                "currency": payment_request.currency,
                "phone_number": payment_request.phone_number,
                "provider": payment_request.provider,
                "callback_url": CALLBACK_URL,
                "reference": f"user_{current_user.id}_order_{payment_request.amount}"
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/callback")
async def mobile_money_callback(request: Request):
    payload = await request.json()
    # Verify the callback signature if required by the provider
    # Process the callback payload to confirm the payment status
    # Update the database or perform necessary actions
    return {"status": "success"}
