"""Email routes for sending notifications."""

from flask import Blueprint, jsonify, request

from app.services.email_service import EmailService

bp = Blueprint("email", __name__, url_prefix="/email")


@bp.route("/send-reminder", methods=["POST"])
def send_reminder():
    """Send a payment reminder email."""
    data = request.get_json()

    try:
        email_service = EmailService()
        result = email_service.send_payment_reminder(
            tenant_email=data["tenant_email"],
            tenant_name=data["tenant_name"],
            property_address=data["property_address"],
            amount_due=float(data["amount_due"]),
            due_date=data["due_date"],
        )
        return jsonify({"success": True, "message_id": result.get("id")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@bp.route("/send-arrears", methods=["POST"])
def send_arrears():
    """Send an arrears notice email."""
    data = request.get_json()

    try:
        email_service = EmailService()
        result = email_service.send_arrears_notice(
            tenant_email=data["tenant_email"],
            tenant_name=data["tenant_name"],
            property_address=data["property_address"],
            amount_owed=float(data["amount_owed"]),
            days_overdue=int(data["days_overdue"]),
        )
        return jsonify({"success": True, "message_id": result.get("id")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@bp.route("/send-receipt", methods=["POST"])
def send_receipt():
    """Send a rent payment receipt email."""
    data = request.get_json()

    try:
        email_service = EmailService()
        result = email_service.send_rent_receipt(
            tenant_email=data["tenant_email"],
            tenant_name=data["tenant_name"],
            property_address=data["property_address"],
            amount_paid=float(data["amount_paid"]),
            payment_date=data["payment_date"],
        )
        return jsonify({"success": True, "message_id": result.get("id")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@bp.route("/test", methods=["GET"])
def test_email():
    """Test email configuration."""
    try:
        email_service = EmailService()
        # Just try to get an access token to verify credentials
        token = email_service._get_access_token()
        return jsonify({"success": True, "message": "Email service configured correctly"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
