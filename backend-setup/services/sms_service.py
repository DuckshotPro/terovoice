"""
SMS service for sending text messages using Twilio.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    logger.warning("Twilio library not found. SMS service will not work.")
    Client = None
    TwilioRestException = None


class SmsService:
    """Service for sending SMS messages."""

    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.enabled = bool(self.account_sid and self.auth_token and self.from_number)

        if self.enabled and Client:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.enabled = False
        else:
            if not Client:
                logger.warning("Twilio library not installed.")
            else:
                logger.warning("Twilio credentials not configured. SMS service disabled.")
            self.client = None

    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send an SMS message to a phone number.

        Args:
            to_number: The recipient's phone number (E.164 format)
            message: The message body

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled or not self.client:
            logger.warning(f"SMS service disabled. skipping message to {to_number}: {message}")
            return False

        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            logger.info(f"SMS sent successfully to {to_number}. SID: {message.sid}")
            return True

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_number}: {str(e)}")
            return False
