"""
Email service for sending notifications throughout the onboarding process.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails."""

    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@tero.com')
        self.from_name = os.getenv('FROM_NAME', 'Tero Voice')

    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None):
        """Send an email using SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add text version if provided
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)

            # Add HTML version
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_welcome_email(self, email: str, name: str, portal_url: str):
        """Send welcome email after PayPal payment completion."""
        subject = "Welcome to Tero Voice - Let's Set Up Your AI Receptionist!"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Tero Voice</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Tero Voice!</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Your AI receptionist is almost ready</p>
            </div>

            <div style="background: white; padding: 30px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">
                <p>Hi {name},</p>

                <p>🎉 <strong>Congratulations!</strong> Your payment has been processed successfully, and you're now part of the Tero Voice family.</p>

                <p>Your AI receptionist is ready to be configured. We'll guide you through a simple 7-step setup process that takes about 10 minutes:</p>

                <ul style="padding-left: 20px;">
                    <li>✅ Business information</li>
                    <li>📞 Phone number setup</li>
                    <li>💬 Custom responses</li>
                    <li>📅 Calendar integration</li>
                    <li>🎤 Interactive demo</li>
                    <li>👀 Review & confirmation</li>
                    <li>🚀 Go live!</li>
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{portal_url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Start Setup Now</a>
                </div>

                <p><strong>What happens next?</strong></p>
                <p>Once you complete the setup, your AI receptionist will be live and ready to handle calls 24/7. You'll receive booking notifications, call transcripts, and detailed analytics.</p>

                <p>Need help? Reply to this email or visit our <a href="https://help.tero.com">help center</a>.</p>

                <p>Welcome aboard!<br>
                The Tero Voice Team</p>
            </div>

            <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                <p>Tero Voice - AI Receptionist Service<br>
                If you have any questions, contact us at support@tero.com</p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to Tero Voice!

        Hi {name},

        Congratulations! Your payment has been processed successfully, and you're now part of the Tero Voice family.

        Your AI receptionist is ready to be configured. We'll guide you through a simple 7-step setup process:

        1. Business information
        2. Phone number setup
        3. Custom responses
        4. Calendar integration
        5. Interactive demo
        6. Review & confirmation
        7. Go live!

        Start your setup here: {portal_url}

        Need help? Reply to this email or visit our help center at https://help.tero.com

        Welcome aboard!
        The Tero Voice Team
        """

        return self._send_email(email, subject, html_body, text_body)

    def send_business_info_confirmation(self, email: str, business_name: str, industry: str):
        """Send confirmation email after business information is saved."""
        subject = f"Business Information Confirmed - {business_name}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #28a745;">
                <h2 style="color: #28a745; margin: 0 0 15px 0;">✅ Business Information Confirmed</h2>

                <p>Great! We've saved your business information:</p>

                <ul style="background: white; padding: 15px; border-radius: 5px; list-style: none;">
                    <li><strong>Business:</strong> {business_name}</li>
                    <li><strong>Industry:</strong> {industry}</li>
                </ul>

                <p>Your AI receptionist is being customized for the {industry.lower()} industry. Next up: phone configuration!</p>

                <p>Questions? Reply to this email anytime.</p>

                <p>Best regards,<br>The Tero Voice Team</p>
            </div>
        </body>
        </html>
        """

        return self._send_email(email, subject, html_body)

    def send_go_live_email(self, email: str, business_name: str):
        """Send congratulations email when onboarding is complete."""
        subject = f"🚀 {business_name} is Live! Your AI Receptionist is Ready"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 30px; text-align: center; border-radius: 10px; color: white;">
                <h1 style="margin: 0; font-size: 32px;">🚀 You're Live!</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px;">Your AI receptionist is now answering calls</p>
            </div>

            <div style="background: white; padding: 30px; border: 1px solid #ddd; margin-top: -1px; border-radius: 0 0 10px 10px;">
                <p>Congratulations! <strong>{business_name}</strong> is now live with Tero Voice.</p>

                <p>🎉 <strong>Your AI receptionist is now:</strong></p>
                <ul>
                    <li>✅ Answering calls 24/7</li>
                    <li>✅ Booking appointments automatically</li>
                    <li>✅ Capturing leads and messages</li>
                    <li>✅ Sending you real-time notifications</li>
                </ul>

                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #495057;">📊 Track Your Success</h3>
                    <p style="margin: 0;">Log into your portal to see call analytics, transcripts, and booking reports. You'll be amazed at how many calls you were missing!</p>
                </div>

                <p><strong>Need Support?</strong></p>
                <ul>
                    <li>📧 Email: support@tero.com</li>
                    <li>📚 Help Center: https://help.tero.com</li>
                    <li>💬 Live Chat: Available in your portal</li>
                </ul>

                <p>Thank you for choosing Tero Voice. Here's to never missing another customer call!</p>

                <p>Best regards,<br>The Tero Voice Team</p>
            </div>
        </body>
        </html>
        """

        return self._send_email(email, subject, html_body)

    def send_error_notification(self, email: str, error_type: str, error_details: str):
        """Send error notification to support team."""
        subject = f"Tero Voice Error: {error_type}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: #dc3545; color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                <h2 style="margin: 0;">⚠️ System Error Detected</h2>
            </div>

            <div style="background: white; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">
                <p><strong>Error Type:</strong> {error_type}</p>
                <p><strong>User Email:</strong> {email}</p>
                <p><strong>Details:</strong></p>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_details}</pre>
                <p><strong>Time:</strong> {datetime.now().isoformat()}</p>
            </div>
        </body>
        </html>
        """

        # Send to support team
        support_email = os.getenv('SUPPORT_EMAIL', 'support@tero.com')
        return self._send_email(support_email, subject, html_body)