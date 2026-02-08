"""
Exception classes for email sending and webhook delivery.

This module defines custom exceptions for classifying email and webhook failures.
"""


class PermanentFailure(Exception):
    """
    Non-retryable failure - email cannot be delivered.
    
    Examples:
    - Invalid recipient (550: User not found)
    - Authentication error
    - Recipient rejected
    - Mailbox name not allowed
    
    Action: Mark job as failed, do NOT retry.
    """
    pass


class TemporaryFailure(Exception):
    """
    Retryable failure - try again later.
    
    Examples:
    - Connection timeout
    - Rate limited (421: Service not available)
    - Server busy (450: Mailbox busy)
    - Insufficient storage (452)
    
    Action: Retry with exponential backoff.
    """
    pass


class WebhookDeliveryError(Exception):
    """
    Retryable webhook delivery error.
    
    Examples:
    - HTTP request timeout
    - Connection error
    - Non-2xx response from webhook endpoint
    
    Action: Retry with exponential backoff up to max_retries.
    """
    pass


# SMTP error code mappings
PERMANENT_SMTP_CODES = {
    550,  # Mailbox unavailable
    551,  # User not local
    552,  # Exceeded storage allocation
    553,  # Mailbox name not allowed
    554,  # Transaction failed
}

TEMPORARY_SMTP_CODES = {
    421,  # Service not available
    450,  # Mailbox busy
    451,  # Local error in processing
    452,  # Insufficient storage
}
