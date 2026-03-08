"""Email service using Google Gmail API."""

import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import urlsafe_b64encode

import requests
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Service for sending emails via Google Gmail API."""

    def __init__(self):
        """Initialize with credentials from environment."""
        self.client_id = os.environ.get("GOOGLE_CLIENT_ID")
        self.client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        self.refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")
        self.from_email = os.environ.get("GOOGLE_EMAIL_FROM")
        self.access_token = None

        # Validate credentials
        if not all([self.client_id, self.client_secret, self.refresh_token, self.from_email]):
            raise ValueError("Missing Google email credentials in environment variables")

    def _get_access_token(self) -> str:
        """Get fresh access token using refresh token."""
        if self.access_token:
            return self.access_token

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(token_url, data=data)
        response.raise_for_status()

        self.access_token = response.json()["access_token"]
        return self.access_token

    def _create_message(
        self, to_email: str, subject: str, html_body: str, text_body: str = None
    ) -> dict:
        """Create a Gmail API message object."""
        message = MIMEMultipart("alternative")
        message["To"] = to_email
        message["From"] = self.from_email
        message["Subject"] = subject

        # Plain text fallback
        if text_body is None:
            text_body = html_body.replace("<br>", "\n").replace("<b>", "").replace("</b>", "")

        message.attach(MIMEText(text_body, "plain"))
        message.attach(MIMEText(html_body, "html"))

        return {
            "raw": urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        }

    def send_email(
        self, to_email: str, subject: str, html_body: str, text_body: str = None
    ) -> dict:
        """Send an email via Gmail API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Optional plain text fallback

        Returns:
            Gmail API response

        Raises:
            requests.HTTPError: If API call fails
        """
        access_token = self._get_access_token()
        message = self._create_message(to_email, subject, html_body, text_body)

        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=message)
        response.raise_for_status()

        return response.json()

    def send_payment_reminder(
        self, tenant_email: str, tenant_name: str, property_address: str, amount_due: float, due_date: str
    ) -> dict:
        """Send a payment reminder email."""
        subject = f"Payment Reminder - {property_address}"
        html_body = f"""
        <html>
        <body>
            <h2>Payment Reminder</h2>
            <p>Dear {tenant_name},</p>
            <p>This is a friendly reminder that your rent payment for:</p>
            <p><b>{property_address}</b></p>
            <p>is due on <b>{due_date}</b></p>
            <p>Amount due: <b>${amount_due:.2f}</b></p>
            <p>Please ensure your payment is submitted on time to avoid late fees.</p>
            <p>Best regards,<br/>RentTrack</p>
        </body>
        </html>
        """

        return self.send_email(tenant_email, subject, html_body)

    def send_arrears_notice(
        self, tenant_email: str, tenant_name: str, property_address: str, amount_owed: float, days_overdue: int
    ) -> dict:
        """Send an arrears notice email."""
        subject = f"IMPORTANT: Arrears Notice - {property_address}"
        html_body = f"""
        <html>
        <body>
            <h2 style="color: red;">Arrears Notice</h2>
            <p>Dear {tenant_name},</p>
            <p>We regret to inform you that your account for:</p>
            <p><b>{property_address}</b></p>
            <p>is now <b>{days_overdue} days overdue</b>.</p>
            <p>Amount owed: <b style="color: red;">${amount_owed:.2f}</b></p>
            <p>Please contact us immediately to arrange payment.</p>
            <p>Failure to respond may result in further action.</p>
            <p>Best regards,<br/>RentTrack</p>
        </body>
        </html>
        """

        return self.send_email(tenant_email, subject, html_body)

    def send_rent_receipt(
        self, tenant_email: str, tenant_name: str, property_address: str, amount_paid: float, payment_date: str
    ) -> dict:
        """Send a rent payment receipt email."""
        subject = f"Rent Payment Receipt - {property_address}"
        html_body = f"""
        <html>
        <body>
            <h2>Payment Receipt</h2>
            <p>Dear {tenant_name},</p>
            <p>We have received your rent payment. Thank you!</p>
            <p><b>Property:</b> {property_address}</p>
            <p><b>Amount Paid:</b> ${amount_paid:.2f}</p>
            <p><b>Date:</b> {payment_date}</p>
            <p>Best regards,<br/>RentTrack</p>
        </body>
        </html>
        """

        return self.send_email(tenant_email, subject, html_body)
