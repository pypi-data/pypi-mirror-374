"""Stripe webhook event processing."""

import json
import logging
from typing import Dict, Any

try:
    import stripe
except ImportError:
    stripe = None

from .credit_manager import CreditManager

logger = logging.getLogger(__name__)


class WebhookProcessor:
    """Process Stripe webhook events."""

    def __init__(self, webhook_secret: str, credit_manager: CreditManager):
        """Initialize with webhook secret and credit manager."""
        self.webhook_secret = webhook_secret
        self.credit_manager = credit_manager

    def verify_and_parse(self, payload: str, signature: str) -> Dict[str, Any]:
        """Verify webhook signature and parse event."""
        if not stripe:
            raise ImportError("stripe package not installed")

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a verified webhook event.
        Returns response data.
        """
        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})

        logger.info(f"Processing webhook event: {event_type}")

        if event_type == "checkout.session.completed":
            return self._handle_checkout_completed(event_data)

        elif event_type == "customer.subscription.created":
            return self._handle_subscription_created(event_data)

        elif event_type == "customer.subscription.updated":
            return self._handle_subscription_updated(event_data)

        elif event_type == "customer.subscription.deleted":
            return self._handle_subscription_deleted(event_data)

        elif event_type == "invoice.payment_succeeded":
            return self._handle_invoice_paid(event_data)

        elif event_type == "invoice.payment_failed":
            return self._handle_invoice_failed(event_data)

        else:
            logger.info(f"Unhandled event type: {event_type}")
            return {"message": f"Event {event_type} received but not processed"}

    def _handle_checkout_completed(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful checkout session for credit purchase."""
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")

        if not user_id:
            logger.error("No user_id in checkout session metadata")
            return {"error": "Missing user_id"}

        # Get line items to determine credits purchased
        if session.get("mode") == "payment":
            # One-time payment for credits
            # In production, fetch line items from Stripe to get price metadata
            # For now, extract from session metadata if available
            credits = int(metadata.get("credits", 0))

            if credits > 0:
                new_balance = self.credit_manager.add_credits(user_id, credits)
                logger.info(f"Added {credits} credits to user {user_id}, new balance: {new_balance}")
                return {"credits_added": credits, "new_balance": new_balance}

        return {"message": "Checkout processed"}

    def _handle_subscription_created(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new subscription creation."""
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        status = subscription.get("status")

        if user_id:
            self.credit_manager.set_subscription_state(
                user_id=user_id,
                status=status,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id
            )
            logger.info(f"Created subscription {subscription_id} for user {user_id}")

        return {"subscription_id": subscription_id, "status": status}

    def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updates (pause/resume/etc)."""
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")
        subscription_id = subscription.get("id")
        status = subscription.get("status")

        if user_id:
            self.credit_manager.set_subscription_state(
                user_id=user_id,
                status=status,
                stripe_subscription_id=subscription_id
            )
            logger.info(f"Updated subscription {subscription_id} status to {status}")

        return {"subscription_id": subscription_id, "status": status}

    def _handle_subscription_deleted(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation."""
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")
        subscription_id = subscription.get("id")

        if user_id:
            self.credit_manager.set_subscription_state(
                user_id=user_id,
                status="cancelled",
                stripe_subscription_id=subscription_id
            )
            logger.info(f"Cancelled subscription {subscription_id} for user {user_id}")

        return {"subscription_id": subscription_id, "status": "cancelled"}

    def _handle_invoice_paid(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful subscription payment."""
        # For monthly subscriptions, could grant monthly credit allotment here
        # For now, just log the payment
        customer_id = invoice.get("customer")
        amount = invoice.get("amount_paid", 0) / 100.0
        logger.info(f"Invoice paid: ${amount} from customer {customer_id}")
        return {"amount_paid": amount}

    def _handle_invoice_failed(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed subscription payment."""
        customer_id = invoice.get("customer")
        logger.warning(f"Invoice payment failed for customer {customer_id}")
        # Could pause subscription or send notification here
        return {"status": "payment_failed"}
