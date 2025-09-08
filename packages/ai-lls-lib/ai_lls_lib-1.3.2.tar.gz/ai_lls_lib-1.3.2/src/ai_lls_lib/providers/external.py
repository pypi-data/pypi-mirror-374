"""
External API provider for production phone verification
"""
import os
from typing import Tuple, Optional
import httpx
from aws_lambda_powertools import Logger
from ..core.models import LineType

logger = Logger()


class ExternalAPIProvider:
    """
    Production provider that calls external verification APIs.
    """

    def __init__(
        self,
        phone_api_key: Optional[str] = None,
        dnc_api_key: Optional[str] = None,
        timeout: float = 10.0
    ):
        """
        Initialize external API provider.

        Args:
            phone_api_key: API key for phone line type verification
            dnc_api_key: API key for DNC list checking
            timeout: HTTP request timeout in seconds
        """
        self.phone_api_key = phone_api_key or os.environ.get("PHONE_VERIFY_API_KEY", "")
        self.dnc_api_key = dnc_api_key or os.environ.get("DNC_API_KEY", "")
        self.http_client = httpx.Client(timeout=timeout)

    def verify_phone(self, phone: str) -> Tuple[LineType, bool]:
        """
        Verify phone using external APIs.

        Args:
            phone: E.164 formatted phone number

        Returns:
            Tuple of (line_type, is_on_dnc_list)

        Raises:
            httpx.HTTPError: For API communication errors
            ValueError: For invalid responses
        """
        line_type = self._check_line_type(phone)
        is_dnc = self._check_dnc(phone)
        return line_type, is_dnc

    def _check_line_type(self, phone: str) -> LineType:
        """
        Check line type via external API.

        TODO: Implement actual API call
        - Use self.phone_api_key for authentication
        - Parse API response
        - Map to LineType enum
        """
        logger.info(f"External line type check for {phone[:6]}***")

        # Placeholder implementation
        # In production, this would make an actual API call
        raise NotImplementedError("External line type API not yet configured")

    def _check_dnc(self, phone: str) -> bool:
        """
        Check DNC status via external API.

        TODO: Implement actual API call
        - Use self.dnc_api_key for authentication
        - Parse API response
        - Return boolean status
        """
        logger.info(f"External DNC check for {phone[:6]}***")

        # Placeholder implementation
        # In production, this would make an actual API call
        raise NotImplementedError("External DNC API not yet configured")

    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, 'http_client'):
            self.http_client.close()
