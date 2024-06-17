from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe
import os
from .. import schemas, models, database, authentication

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(authentication.get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/create-payment-intent", response_model=dict)
def create_payment_intent(
    request: schemas.CreatePaymentIntentRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(authentication.get_current_active_user),
):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency,
            payment_method=request.payment_method,
            confirmation_method='manual',
            confirm=True
        )
        return {"client_secret": payment_intent.client_secret}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook", response_model=dict)
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_intent_succeeded(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_intent_failed(payment_intent)

    return {"status": "success"}

def handle_payment_intent_succeeded(payment_intent):
    # Fulfill the purchase
    print("PaymentIntent was successful!")
    # Add logic to handle successful payment (e.g., update database, send email)

def handle_payment_intent_failed(payment_intent):
    # Notify the customer that the order was not fulfilled
    print("PaymentIntent failed.")
    # Add logic to handle failed payment (e.g., notify user)
