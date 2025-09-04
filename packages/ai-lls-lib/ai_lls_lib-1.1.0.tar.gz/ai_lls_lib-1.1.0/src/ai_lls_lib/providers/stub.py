"""
Stub provider for development and testing
"""
from typing import Tuple
from aws_lambda_powertools import Logger
from ..core.models import LineType

logger = Logger()


class StubProvider:
    """
    Stub implementation for development and testing.
    Uses deterministic rules based on phone number digits.
    """

    def verify_phone(self, phone: str) -> Tuple[LineType, bool]:
        """
        Verify using stub logic based on last digit.

        Line type:
        - Ends in 2 or 0: LANDLINE
        - Otherwise: MOBILE

        DNC status:
        - Ends in 1 or 0: on DNC list
        - Otherwise: not on DNC

        Args:
            phone: E.164 formatted phone number

        Returns:
            Tuple of (line_type, is_on_dnc_list)
        """
        logger.info(f"Stub verification for {phone[:6]}***")

        last_digit = phone[-1] if phone else '5'

        # Determine line type
        if last_digit in ['2', '0']:
            line_type = LineType.LANDLINE
        else:
            line_type = LineType.MOBILE

        # Determine DNC status
        is_dnc = last_digit in ['1', '0']

        return line_type, is_dnc
