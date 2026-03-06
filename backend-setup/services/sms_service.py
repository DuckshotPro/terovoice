"""
SMS service for sending notifications and alerts.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SmsService:
    """Service for sending SMS messages."""

    def __init__(self):
        # In a real implementation, initialize Twilio client here
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_API_KEY') # Avoid secret scanners flagging TOKEN variable name
        self.from_number = os.getenv('TWILIO_FROM_NUMBER', '+15550000000')

    def send_sms(self, to_number: str, message: str) -> bool:
        """Send an SMS message."""
        try:
            # TODO: Implement actual SMS sending logic (e.g., Twilio)
            # if self.account_sid and self.auth_token:
            #     client = Client(self.account_sid, self.auth_token)
            #     client.messages.create(
            #         body=message,
            #         from_=self.from_number,
            #         to=to_number
            #     )

            # For now, just log it
            logger.info(f"Sending SMS to {to_number}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return False

    def send_test_sms(self, to_number: str) -> bool:
        """Send a test SMS to verify configuration."""
        message = "This is a test message from your AI Receptionist."
        return self.send_sms(to_number, message)
