"""Credit balance management with DynamoDB."""

import os
from typing import Optional, Dict, Any
from decimal import Decimal
import logging
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None  # Handle gracefully for testing

logger = logging.getLogger(__name__)


class CreditManager:
    """
    Manages user credit balances in DynamoDB CreditsTable.
    """

    def __init__(self, table_name: Optional[str] = None):
        """Initialize with DynamoDB table."""
        if not boto3:
            logger.warning("boto3 not installed, using mock credit manager")
            self.table = None
            return

        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = table_name or os.environ.get("CREDITS_TABLE", "CreditsTable")

        try:
            self.table = self.dynamodb.Table(self.table_name)
        except Exception as e:
            logger.error(f"Failed to connect to DynamoDB table {self.table_name}: {e}")
            self.table = None

    def get_balance(self, user_id: str) -> int:
        """Get current credit balance for a user."""
        if not self.table:
            return 1000  # Mock balance for testing

        try:
            response = self.table.get_item(Key={"user_id": user_id})
            if "Item" in response:
                return int(response["Item"].get("credits", 0))
            return 0
        except ClientError as e:
            logger.error(f"Error getting balance for {user_id}: {e}")
            return 0

    def add_credits(self, user_id: str, amount: int) -> int:
        """Add credits to user balance and return new balance."""
        if not self.table:
            return 1000 + amount  # Mock for testing

        try:
            response = self.table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="ADD credits :amount SET updated_at = :now",
                ExpressionAttributeValues={
                    ":amount": Decimal(amount),
                    ":now": datetime.utcnow().isoformat()
                },
                ReturnValues="ALL_NEW"
            )
            return int(response["Attributes"]["credits"])
        except ClientError as e:
            logger.error(f"Error adding credits for {user_id}: {e}")
            raise

    def deduct_credits(self, user_id: str, amount: int) -> bool:
        """
        Deduct credits from user balance.
        Returns True if successful, False if insufficient balance.
        """
        if not self.table:
            return True  # Mock for testing

        try:
            # Conditional update - only deduct if balance >= amount
            self.table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="ADD credits :negative_amount SET updated_at = :now",
                ConditionExpression="credits >= :amount",
                ExpressionAttributeValues={
                    ":negative_amount": Decimal(-amount),
                    ":amount": Decimal(amount),
                    ":now": datetime.utcnow().isoformat()
                }
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                logger.info(f"Insufficient credits for {user_id}")
                return False
            logger.error(f"Error deducting credits for {user_id}: {e}")
            raise

    def set_subscription_state(
        self,
        user_id: str,
        status: str,
        stripe_customer_id: Optional[str] = None,
        stripe_subscription_id: Optional[str] = None
    ) -> None:
        """Update subscription state in CreditsTable."""
        if not self.table:
            return  # Mock for testing

        try:
            update_expr = "SET subscription_status = :status, updated_at = :now"
            expr_values = {
                ":status": status,
                ":now": datetime.utcnow().isoformat()
            }

            if stripe_customer_id:
                update_expr += ", stripe_customer_id = :customer_id"
                expr_values[":customer_id"] = stripe_customer_id

            if stripe_subscription_id:
                update_expr += ", stripe_subscription_id = :subscription_id"
                expr_values[":subscription_id"] = stripe_subscription_id

            self.table.update_item(
                Key={"user_id": user_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values
            )
        except ClientError as e:
            logger.error(f"Error updating subscription state for {user_id}: {e}")
            raise

    def get_user_payment_info(self, user_id: str) -> Dict[str, Any]:
        """Get user's payment-related information."""
        if not self.table:
            return {
                "credits": 1000,
                "stripe_customer_id": None,
                "stripe_subscription_id": None,
                "subscription_status": None
            }

        try:
            response = self.table.get_item(Key={"user_id": user_id})
            if "Item" in response:
                item = response["Item"]
                return {
                    "credits": int(item.get("credits", 0)),
                    "stripe_customer_id": item.get("stripe_customer_id"),
                    "stripe_subscription_id": item.get("stripe_subscription_id"),
                    "subscription_status": item.get("subscription_status")
                }
            return {
                "credits": 0,
                "stripe_customer_id": None,
                "stripe_subscription_id": None,
                "subscription_status": None
            }
        except ClientError as e:
            logger.error(f"Error getting payment info for {user_id}: {e}")
            return {
                "credits": 0,
                "stripe_customer_id": None,
                "stripe_subscription_id": None,
                "subscription_status": None
            }

    def has_unlimited_access(self, user_id: str) -> bool:
        """Check if user has unlimited access via active subscription."""
        info = self.get_user_payment_info(user_id)
        return info.get("subscription_status") == "active"

    def set_stripe_customer_id(self, user_id: str, stripe_customer_id: str) -> None:
        """Store Stripe customer ID for a user."""
        if not self.table:
            return  # Mock for testing

        try:
            self.table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET stripe_customer_id = :customer_id, updated_at = :now",
                ExpressionAttributeValues={
                    ":customer_id": stripe_customer_id,
                    ":now": datetime.utcnow().isoformat()
                }
            )
            logger.info(f"Stored Stripe customer ID {stripe_customer_id} for user {user_id}")
        except ClientError as e:
            logger.error(f"Error storing Stripe customer ID for {user_id}: {e}")
            raise
