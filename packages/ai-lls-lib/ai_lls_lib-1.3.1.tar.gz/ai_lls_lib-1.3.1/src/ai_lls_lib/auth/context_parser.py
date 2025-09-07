"""Auth context parser for HTTP API v2.0 events."""
from typing import Any, Dict, Optional


def get_user_from_event(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract user ID from HTTP API v2.0 event with all possible paths.
    Handles both JWT and API key authentication contexts.

    This function handles the complexities of AWS API Gateway authorizer contexts,
    especially when EnableSimpleResponses is set to false, which wraps the
    context in a 'lambda' key.

    Args:
        event: The Lambda event from API Gateway HTTP API v2.0

    Returns:
        User ID string if found, None otherwise
    """
    request_context = event.get("requestContext", {})
    auth = request_context.get("authorizer", {})

    # Handle lambda-wrapped context (EnableSimpleResponses: false)
    # When EnableSimpleResponses is false, the authorizer context is wrapped
    lam_ctx = auth.get("lambda", auth) if isinstance(auth.get("lambda"), dict) else auth

    # Try all possible paths for user_id in priority order
    user_id = (
        # Lambda authorizer paths (most common with current setup)
        lam_ctx.get("principal_id") or
        lam_ctx.get("principalId") or
        lam_ctx.get("sub") or
        lam_ctx.get("user_id") or
        # JWT paths (when using JWT authorizer directly)
        auth.get("jwt", {}).get("claims", {}).get("sub") or
        # Direct auth paths (fallback)
        auth.get("principal_id") or
        auth.get("principalId") or
        auth.get("sub")
    )

    return user_id


def get_email_from_event(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract email from HTTP API v2.0 event.

    Args:
        event: The Lambda event from API Gateway HTTP API v2.0

    Returns:
        Email string if found, None otherwise
    """
    request_context = event.get("requestContext", {})
    auth = request_context.get("authorizer", {})

    # Handle lambda-wrapped context
    lam_ctx = auth.get("lambda", auth) if isinstance(auth.get("lambda"), dict) else auth

    # Try to get email from various locations
    email = (
        lam_ctx.get("email") or
        auth.get("jwt", {}).get("claims", {}).get("email") or
        auth.get("email")
    )

    return email
