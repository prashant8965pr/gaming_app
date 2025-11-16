"""
Email Notification Service
Handles sending transactional emails using SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import List, Optional, Dict
from jinja2 import Template
import os
from pathlib import Path

from config.settings import settings


class EmailService:
    """Service for sending emails"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM
        self.from_name = settings.SMTP_FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send an email

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            attachments: List of attachments (optional)

        Returns:
            bool: True if email sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Attach text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)

            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    # Handle different attachment types
                    pass  # Can be implemented later

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)

                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)

                server.sendmail(self.from_email, recipients, msg.as_string())

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    async def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email to new user"""
        subject = f"Welcome to {self.from_name}!"

        html_body = self._render_template('welcome', {
            'username': username,
            'app_name': self.from_name
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_kyc_approved_email(
        self,
        to_email: str,
        username: str
    ) -> bool:
        """Send KYC approval notification"""
        subject = "KYC Verification Approved"

        html_body = self._render_template('kyc_approved', {
            'username': username
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_kyc_rejected_email(
        self,
        to_email: str,
        username: str,
        reason: str
    ) -> bool:
        """Send KYC rejection notification"""
        subject = "KYC Verification - Action Required"

        html_body = self._render_template('kyc_rejected', {
            'username': username,
            'reason': reason
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_deposit_confirmation_email(
        self,
        to_email: str,
        username: str,
        amount: float,
        transaction_id: str
    ) -> bool:
        """Send deposit confirmation"""
        subject = "Deposit Successful"

        html_body = self._render_template('deposit_confirmation', {
            'username': username,
            'amount': amount,
            'transaction_id': transaction_id
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_withdrawal_confirmation_email(
        self,
        to_email: str,
        username: str,
        amount: float,
        transaction_id: str
    ) -> bool:
        """Send withdrawal initiation confirmation"""
        subject = "Withdrawal Request Received"

        html_body = self._render_template('withdrawal_initiated', {
            'username': username,
            'amount': amount,
            'transaction_id': transaction_id
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_withdrawal_completed_email(
        self,
        to_email: str,
        username: str,
        amount: float,
        utr_number: str
    ) -> bool:
        """Send withdrawal completion notification"""
        subject = "Withdrawal Completed"

        html_body = self._render_template('withdrawal_completed', {
            'username': username,
            'amount': amount,
            'utr_number': utr_number
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_game_win_email(
        self,
        to_email: str,
        username: str,
        game_name: str,
        winnings: float
    ) -> bool:
        """Send game win notification"""
        subject = f"Congratulations! You won ₹{winnings}"

        html_body = self._render_template('game_win', {
            'username': username,
            'game_name': game_name,
            'winnings': winnings
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_referral_bonus_email(
        self,
        to_email: str,
        username: str,
        bonus_amount: float,
        referred_user: str
    ) -> bool:
        """Send referral bonus notification"""
        subject = "Referral Bonus Credited!"

        html_body = self._render_template('referral_bonus', {
            'username': username,
            'bonus_amount': bonus_amount,
            'referred_user': referred_user
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_2fa_enabled_email(
        self,
        to_email: str,
        username: str
    ) -> bool:
        """Send 2FA enabled notification"""
        subject = "Two-Factor Authentication Enabled"

        html_body = self._render_template('2fa_enabled', {
            'username': username
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_link: str
    ) -> bool:
        """Send password reset email"""
        subject = "Password Reset Request"

        html_body = self._render_template('password_reset', {
            'username': username,
            'reset_link': reset_link
        })

        return await self.send_email(to_email, subject, html_body)

    async def send_promo_code_email(
        self,
        to_email: str,
        username: str,
        promo_code: str,
        discount: str,
        expiry_date: str
    ) -> bool:
        """Send promo code email"""
        subject = f"Exclusive Promo Code: {promo_code}"

        html_body = self._render_template('promo_code', {
            'username': username,
            'promo_code': promo_code,
            'discount': discount,
            'expiry_date': expiry_date
        })

        return await self.send_email(to_email, subject, html_body)

    def _render_template(self, template_name: str, context: dict) -> str:
        """Render email template with context"""
        # Get template
        template_content = self._get_template(template_name)

        # Render with Jinja2
        template = Template(template_content)
        return template.render(**context)

    def _get_template(self, template_name: str) -> str:
        """Get email template"""
        # Try to load from file
        template_file = Path(f"templates/emails/{template_name}.html")

        if template_file.exists():
            return template_file.read_text()

        # Fallback to basic templates
        return EMAIL_TEMPLATES.get(template_name, EMAIL_TEMPLATES['default'])


# Basic email templates (can be moved to separate HTML files)
EMAIL_TEMPLATES = {
    'default': """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gaming Platform</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            {{ content }}
        </div>
    </body>
    </html>
    """,

    'welcome': """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Welcome</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
            <h1 style="color: #4CAF50;">Welcome to {{ app_name }}!</h1>
            <p>Hi {{ username }},</p>
            <p>Welcome to our gaming platform! We're excited to have you join our community.</p>
            <p>Here's what you can do next:</p>
            <ul>
                <li>Complete your KYC verification to unlock all features</li>
                <li>Add funds to your wallet</li>
                <li>Browse our game catalog and start playing</li>
                <li>Invite friends and earn referral bonuses</li>
            </ul>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <p>Happy gaming!</p>
            <p style="margin-top: 30px;">Best regards,<br>The {{ app_name }} Team</p>
        </div>
    </body>
    </html>
    """,

    'kyc_approved': """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>KYC Approved</title></head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
            <h1 style="color: #4CAF50;">✓ KYC Verification Approved</h1>
            <p>Hi {{ username }},</p>
            <p>Great news! Your KYC verification has been approved.</p>
            <p>You can now access all features of the platform, including withdrawals.</p>
            <p>Thank you for completing the verification process!</p>
        </div>
    </body>
    </html>
    """,

    'kyc_rejected': """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>KYC Action Required</title></head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
            <h1 style="color: #f44336;">KYC Verification - Action Required</h1>
            <p>Hi {{ username }},</p>
            <p>Unfortunately, we were unable to verify your KYC documents.</p>
            <p><strong>Reason:</strong> {{ reason }}</p>
            <p>Please resubmit your documents with the corrections.</p>
            <p>If you have questions, please contact our support team.</p>
        </div>
    </body>
    </html>
    """,

    'deposit_confirmation': """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Deposit Successful</title></head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
            <h1 style="color: #4CAF50;">✓ Deposit Successful</h1>
            <p>Hi {{ username }},</p>
            <p>Your deposit of <strong>₹{{ amount }}</strong> has been successfully credited to your account.</p>
            <p>Transaction ID: <strong>{{ transaction_id }}</strong></p>
            <p>You can now use these funds to play games!</p>
        </div>
    </body>
    </html>
    """,

    'withdrawal_completed': """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Withdrawal Completed</title></head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
            <h1 style="color: #4CAF50;">✓ Withdrawal Completed</h1>
            <p>Hi {{ username }},</p>
            <p>Your withdrawal of <strong>₹{{ amount }}</strong> has been completed.</p>
            <p>UTR Number: <strong>{{ utr_number }}</strong></p>
            <p>The amount should reflect in your bank account within 1-3 business days.</p>
        </div>
    </body>
    </html>
    """,

    'game_win': """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Congratulations!</title></head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
            <h1 style="color: #FFD700;">🎉 Congratulations!</h1>
            <p>Hi {{ username }},</p>
            <p>You won <strong>₹{{ winnings }}</strong> in {{ game_name }}!</p>
            <p>Your winnings have been credited to your Winnings Wallet.</p>
            <p>Keep playing and winning!</p>
        </div>
    </body>
    </html>
    """,

    '2fa_enabled': """
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>2FA Enabled</title></head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
            <h1 style="color: #4CAF50;">🔒 Two-Factor Authentication Enabled</h1>
            <p>Hi {{ username }},</p>
            <p>Two-factor authentication has been successfully enabled on your account.</p>
            <p>Your account is now more secure. You'll need to enter a code from your authenticator app when logging in.</p>
            <p>If you didn't enable this, please contact our support team immediately.</p>
        </div>
    </body>
    </html>
    """
}


# Global email service instance
email_service = EmailService()
