"""Interior Design Matching Platform - Flask application factory."""
import os
from pathlib import Path

from flask import Flask, redirect, session, url_for

import db
from boundary.access_control import dashboard_for
from boundary.login_page import login_bp
from boundary.user_account_pages import user_account_bp
from boundary.user_profile_pages import user_profile_bp
from boundary.company_pages import company_bp
from boundary.category_pages import category_bp
from boundary.idp_pages import idp_bp
from boundary.customer_pages import customer_bp
from boundary.tracking_pages import tracking_bp
from boundary.report_pages import report_bp

BASE_DIR = Path(__file__).resolve().parent


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get("DATABASE", str(BASE_DIR / "instance" / "idp_platform.db")),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    if not Path(app.config["DATABASE"]).exists():
        db.init_db(app.config["DATABASE"])

    app.teardown_appcontext(db.close_connection)

    app.register_blueprint(login_bp)
    app.register_blueprint(user_account_bp)
    app.register_blueprint(user_profile_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(idp_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(report_bp)

    @app.route("/")
    def home():
        if not session.get("account_id"):
            return redirect(url_for("login.displayLoginPage"))
        return redirect(url_for(dashboard_for(session.get("role"))))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
