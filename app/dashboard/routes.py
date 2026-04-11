from __future__ import annotations

from flask import Flask, render_template

from app.dashboard.template_filters import register_filters
from app.database.db import fetch_counts, fetch_recent_logs, fetch_top_users


def create_dashboard_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    register_filters(app)

    @app.route("/")
    def index() -> str:
        counts = fetch_counts()
        recent_logs = fetch_recent_logs(limit=10)
        top_users = fetch_top_users(limit=5)
        return render_template(
            "index.html",
            counts=counts,
            recent_logs=recent_logs,
            top_users=top_users,
        )

    @app.route("/messages")
    def messages() -> str:
        logs = fetch_recent_logs(limit=100)
        return render_template("messages.html", logs=logs)

    return app
