"""Test script for the email service."""

from src.app.services.email_service import EmailService


def test_send_email():
    """Test basic email sending."""
    email_service = EmailService()
    result = email_service.send_email(
        to_email="sunjie5678@gmail.com",
        subject="Test Email",
        html_body="<h1>Hello!</h1><p>This is a test email from the RentTrack app.</p>"
    )
    print("Email sent successfully!")
    print(f"Message ID: {result.get('id')}")
    return result


def test_payment_reminder():
    """Test payment reminder email."""
    email_service = EmailService()
    result = email_service.send_payment_reminder(
        tenant_email="tenant@example.com",
        tenant_name="John Doe",
        property_address="123 Main St, Toronto, ON",
        amount_due=1500.00,
        due_date="March 15, 2026"
    )
    print("Payment reminder sent successfully!")
    print(f"Message ID: {result.get('id')}")
    return result


def test_arrears_notice():
    """Test arrears notice email."""
    email_service = EmailService()
    result = email_service.send_arrears_notice(
        tenant_email="tenant@example.com",
        tenant_name="John Doe",
        property_address="123 Main St, Toronto, ON",
        amount_owed=1500.00,
        days_overdue=15
    )
    print("Arrears notice sent successfully!")
    print(f"Message ID: {result.get('id')}")
    return result


def test_rent_receipt():
    """Test rent receipt email."""
    email_service = EmailService()
    result = email_service.send_rent_receipt(
        tenant_email="tenant@example.com",
        tenant_name="John Doe",
        property_address="123 Main St, Toronto, ON",
        amount_paid=1500.00,
        payment_date="March 1, 2026"
    )
    print("Rent receipt sent successfully!")
    print(f"Message ID: {result.get('id')}")
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test_email.py [basic|reminder|arrears|receipt]")
        print("  basic   - Test basic email sending")
        print("  reminder - Test payment reminder email")
        print("  arrears - Test arrears notice email")
        print("  receipt  - Test rent receipt email")
        sys.exit(1)

    test_type = sys.argv[1].lower()

    if test_type == "basic":
        test_send_email()
    elif test_type == "reminder":
        test_payment_reminder()
    elif test_type == "arrears":
        test_arrears_notice()
    elif test_type == "receipt":
        test_rent_receipt()
    else:
        print(f"Unknown test type: {test_type}")
        sys.exit(1)
