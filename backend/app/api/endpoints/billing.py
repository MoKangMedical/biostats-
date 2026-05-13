"""
Stripe payment endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field

from app.api.endpoints.users import get_current_user
from app.models.user import User, SubscriptionTier
from app.services.stripe_service import StripeService

router = APIRouter()


# Request/Response models
class CheckoutRequest(BaseModel):
    plan: str = Field(..., description="Subscription plan: pro or enterprise")
    success_url: str = Field(default="https://mokangmedical.github.io/Biostats/success", description="Success redirect URL")
    cancel_url: str = Field(default="https://mokangmedical.github.io/Biostats/pricing", description="Cancel redirect URL")


class CheckoutResponse(BaseModel):
    session_id: str = None
    url: str
    plan: str
    price: int = None
    message: str


class PortalResponse(BaseModel):
    session_id: str
    url: str
    message: str


class PlansResponse(BaseModel):
    plans: Dict[str, Any]


class UsageResponse(BaseModel):
    allowed: bool
    remaining: Any
    limit: Any
    used: int
    message: str


# Endpoints
@router.get("/plans", response_model=PlansResponse)
async def get_plans():
    """
    Get available subscription plans
    
    Returns details about Free, Pro, and Enterprise plans.
    """
    plans = StripeService.get_plans()
    return PlansResponse(plans=plans)


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create Stripe checkout session
    
    Redirects user to Stripe checkout to complete payment.
    """
    try:
        # Validate plan
        try:
            plan = SubscriptionTier(request.plan)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan: {request.plan}. Must be 'pro' or 'enterprise'."
            )
        
        if plan == SubscriptionTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot checkout for free plan"
            )
        
        result = StripeService.create_checkout_session(
            user_id=current_user.id,
            plan=plan,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
        
        return CheckoutResponse(
            session_id=result.get("session_id"),
            url=result["url"],
            plan=result.get("plan"),
            price=result.get("price"),
            message=result["message"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Checkout error: {str(e)}"
        )


@router.post("/portal", response_model=PortalResponse)
async def create_portal(
    return_url: str = "https://mokangmedical.github.io/Biostats/account",
    current_user: User = Depends(get_current_user)
):
    """
    Create Stripe customer portal session
    
    Allows user to manage their subscription, update payment method, etc.
    """
    try:
        result = StripeService.create_customer_portal(
            user_id=current_user.id,
            return_url=return_url
        )
        
        return PortalResponse(
            session_id=result["session_id"],
            url=result["url"],
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Portal error: {str(e)}"
        )


@router.get("/usage", response_model=UsageResponse)
async def check_usage(
    current_user: User = Depends(get_current_user)
):
    """
    Check current usage and limits
    
    Returns remaining analyses for the current billing period.
    """
    result = StripeService.check_usage_limits(
        user_subscription=current_user.subscription_tier,
        analyses_this_month=current_user.analyses_this_month
    )
    
    return UsageResponse(
        allowed=result["allowed"],
        remaining=result["remaining"],
        limit=result["limit"],
        used=result["used"],
        message=result["message"]
    )


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    
    Processes payment confirmations, subscription updates, etc.
    """
    try:
        # Get webhook payload
        payload = await request.body()
        
        # In production, verify webhook signature here
        # sig_header = request.headers.get("stripe-signature")
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        # For now, parse as JSON (in production, use Stripe's webhook verification)
        import json
        event = json.loads(payload)
        
        result = StripeService.handle_webhook(event)
        
        return {"status": result["status"], "message": f"Webhook processed: {result.get('action', 'unknown')}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )
