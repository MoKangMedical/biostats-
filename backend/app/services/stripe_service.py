"""
Stripe payment integration service
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.user import SubscriptionTier


class StripeService:
    """Service for Stripe payment integration"""
    
    # Subscription plans
    PLANS = {
        SubscriptionTier.FREE: {
            "name": "Free",
            "price": 0,
            "analyses_per_month": 10,
            "features": [
                "Basic statistical tests",
                "Simple visualizations",
                "10 analyses per month",
                "Community support"
            ]
        },
        SubscriptionTier.PRO: {
            "name": "Pro",
            "price": 99,
            "stripe_price_id": "price_pro_monthly",  # Replace with actual Stripe price ID
            "analyses_per_month": -1,  # Unlimited
            "features": [
                "All statistical tests",
                "Advanced visualizations",
                "Unlimited analyses",
                "AI interpretations",
                "Publication-ready exports",
                "Priority support"
            ]
        },
        SubscriptionTier.ENTERPRISE: {
            "name": "Enterprise",
            "price": 499,
            "stripe_price_id": "price_enterprise_monthly",  # Replace with actual Stripe price ID
            "analyses_per_month": -1,  # Unlimited
            "features": [
                "Everything in Pro",
                "Multi-user collaboration",
                "Custom branding",
                "API access",
                "Dedicated support",
                "Training sessions",
                "SLA guarantee"
            ]
        }
    }
    
    @staticmethod
    def get_plans() -> Dict[str, Any]:
        """Get available subscription plans"""
        return StripeService.PLANS
    
    @staticmethod
    def create_checkout_session(
        user_id: int,
        plan: SubscriptionTier,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create Stripe checkout session
        
        In production, this would use the Stripe SDK to create a session.
        For now, returns a mock response.
        """
        plan_details = StripeService.PLANS.get(plan)
        if not plan_details:
            raise ValueError(f"Invalid plan: {plan}")
        
        if plan == SubscriptionTier.FREE:
            return {
                "session_id": None,
                "url": success_url,
                "message": "Free plan activated"
            }
        
        # Mock Stripe session (replace with actual Stripe integration)
        return {
            "session_id": f"cs_mock_{user_id}_{plan.value}",
            "url": f"https://checkout.stripe.com/pay/cs_mock_{user_id}_{plan.value}",
            "plan": plan.value,
            "price": plan_details["price"],
            "message": "Redirect to Stripe checkout"
        }
    
    @staticmethod
    def create_customer_portal(
        user_id: int,
        return_url: str
    ) -> Dict[str, Any]:
        """
        Create Stripe customer portal session
        
        In production, this would use the Stripe SDK.
        """
        # Mock portal session (replace with actual Stripe integration)
        return {
            "session_id": f"portal_mock_{user_id}",
            "url": f"https://billing.stripe.com/session/portal_mock_{user_id}",
            "message": "Redirect to customer portal"
        }
    
    @staticmethod
    def handle_webhook(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Stripe webhook events
        
        In production, this would verify the webhook signature and process events.
        """
        event_type = event.get("type")
        
        if event_type == "checkout.session.completed":
            # Payment successful
            session = event["data"]["object"]
            customer_id = session.get("customer")
            subscription_id = session.get("subscription")
            
            return {
                "status": "success",
                "action": "activate_subscription",
                "customer_id": customer_id,
                "subscription_id": subscription_id
            }
        
        elif event_type == "invoice.paid":
            # Subscription renewed
            invoice = event["data"]["object"]
            customer_id = invoice.get("customer")
            
            return {
                "status": "success",
                "action": "renew_subscription",
                "customer_id": customer_id
            }
        
        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled
            subscription = event["data"]["object"]
            customer_id = subscription.get("customer")
            
            return {
                "status": "success",
                "action": "cancel_subscription",
                "customer_id": customer_id
            }
        
        else:
            return {
                "status": "ignored",
                "event_type": event_type
            }
    
    @staticmethod
    def check_usage_limits(user_subscription: SubscriptionTier, analyses_this_month: int) -> Dict[str, Any]:
        """
        Check if user has exceeded usage limits
        
        Returns:
            Dictionary with usage status and limits
        """
        plan = StripeService.PLANS.get(user_subscription)
        if not plan:
            return {"allowed": False, "message": "Invalid subscription"}
        
        monthly_limit = plan["analyses_per_month"]
        
        if monthly_limit == -1:  # Unlimited
            return {
                "allowed": True,
                "remaining": "unlimited",
                "limit": "unlimited"
            }
        
        remaining = max(0, monthly_limit - analyses_this_month)
        
        return {
            "allowed": remaining > 0,
            "remaining": remaining,
            "limit": monthly_limit,
            "used": analyses_this_month,
            "message": f"{remaining} analyses remaining this month" if remaining > 0 else "Monthly limit reached"
        }
