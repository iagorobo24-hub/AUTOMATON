from fastapi import APIRouter, HTTPException, Depends, Request
import os
import uuid
import logging
from datetime import datetime, timezone
from ..services.database import DatabaseService
from ..api.deps import get_db_service
from ..core.config import settings

router = APIRouter()

@router.post("/create-session")
async def create_payment_session(
    request: Request, 
    amount: float, 
    package_type: str = "custom",
    db_service: DatabaseService = Depends(get_db_service)
):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    api_key = settings.STRIPE_API_KEY or os.environ.get('STRIPE_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    origin = request.headers.get("origin", str(request.base_url).rstrip("/"))
    success_url = f"{origin}/wallet?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin}/wallet"
    
    webhook_url = f"{str(request.base_url).rstrip('/')}/api/payments/webhook"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    checkout_request = CheckoutSessionRequest(
        amount=float(amount),
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"package_type": package_type, "type": "agent_funding"},
        payment_methods=["card", "crypto"]
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db_service.db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "type": "stripe",
        "amount": amount,
        "currency": "USD",
        "status": "pending",
        "stripe_session_id": session.session_id,
        "metadata": {"package_type": package_type},
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@router.get("/status/{session_id}")
async def get_payment_status(
    session_id: str,
    db_service: DatabaseService = Depends(get_db_service)
):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = settings.STRIPE_API_KEY
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url="")
    
    status = await stripe_checkout.get_checkout_status(session_id)
    
    await db_service.db.payment_transactions.update_one(
        {"stripe_session_id": session_id},
        {"$set": {"status": status.payment_status}}
    )
    
    return {
        "session_id": session_id,
        "status": status.status,
        "payment_status": status.payment_status,
        "amount": status.amount_total / 100,
        "currency": status.currency
    }

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db_service: DatabaseService = Depends(get_db_service)
):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = settings.STRIPE_API_KEY
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url="")
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            await db_service.db.payment_transactions.update_one(
                {"stripe_session_id": webhook_response.session_id},
                {"$set": {"status": "completed"}}
            )
        
        return {"received": True}
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return {"received": True}

@router.get("/transactions")
async def get_transactions(
    db_service: DatabaseService = Depends(get_db_service)
):
    transactions = await db_service.db.payment_transactions.find({}, {"_id": 0}).to_list(100)
    return {"transactions": transactions}
