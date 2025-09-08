"""
Phone verification logic - checks line type and DNC status
"""
import os
from datetime import datetime, timezone
from typing import Optional
import phonenumbers
from aws_lambda_powertools import Logger
from .models import PhoneVerification, LineType, VerificationSource
from .cache import DynamoDBCache
from ..providers import VerificationProvider, StubProvider

logger = Logger()


class PhoneVerifier:
    """Verifies phone numbers for line type and DNC status"""

    def __init__(self, cache: DynamoDBCache, provider: Optional[VerificationProvider] = None):
        """
        Initialize phone verifier.

        Args:
            cache: DynamoDB cache for storing results
            provider: Verification provider (defaults to StubProvider)
        """
        self.cache = cache
        self.provider = provider or StubProvider()

    def normalize_phone(self, phone: str) -> str:
        """Normalize phone to E.164 format"""
        try:
            # Parse with US as default country
            parsed = phonenumbers.parse(phone, "US")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError(f"Invalid phone number: {phone}")

            # Format as E.164
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            logger.error(f"Phone normalization failed: {str(e)}")
            raise ValueError(f"Invalid phone format: {phone}")

    def verify(self, phone: str) -> PhoneVerification:
        """Verify phone number for line type and DNC status"""
        normalized = self.normalize_phone(phone)

        # Check cache first
        cached = self.cache.get(normalized)
        if cached:
            return cached

        # Use provider to verify
        line_type, dnc_status = self.provider.verify_phone(normalized)

        result = PhoneVerification(
            phone_number=normalized,
            line_type=line_type,
            dnc=dnc_status,
            cached=False,
            verified_at=datetime.now(timezone.utc),
            source=VerificationSource.API
        )

        # Store in cache
        self.cache.set(normalized, result)

        return result

    def _check_line_type(self, phone: str) -> LineType:
        """
        Check line type (for backwards compatibility with CLI).
        Delegates to provider.
        """
        line_type, _ = self.provider.verify_phone(phone)
        return line_type

    def _check_dnc(self, phone: str) -> bool:
        """
        Check DNC status (for backwards compatibility with CLI).
        Delegates to provider.
        """
        _, dnc_status = self.provider.verify_phone(phone)
        return dnc_status
