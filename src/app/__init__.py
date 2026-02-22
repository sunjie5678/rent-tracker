"""Flask application factory."""

import os

from flask import Flask

from app.config import config_by_name
from app.database import db_session, shutdown_session


def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(config_by_name[config_name])

    # Teardown database session after each request
    app.teardown_appcontext(shutdown_session)

    # Register blueprints
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.properties import bp as properties_bp
    from app.routes.tenants import bp as tenants_bp
    from app.routes.payments import bp as payments_bp
    from app.routes.allocations import bp as allocations_bp
    from app.routes.rent_charges import bp as rent_charges_bp
    from app.routes.reports import bp as reports_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(properties_bp, url_prefix="/properties")
    app.register_blueprint(tenants_bp, url_prefix="/tenants")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(allocations_bp, url_prefix="/allocations")
    app.register_blueprint(rent_charges_bp, url_prefix="/rent-charges")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    # Template globals
    from app.models.rent_charge import ChargeStatus

    app.jinja_env.globals["ChargeStatus"] = ChargeStatus

    return app
