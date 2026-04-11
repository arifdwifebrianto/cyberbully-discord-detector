from __future__ import annotations

import threading

from app.config import settings
from app.dashboard.routes import create_dashboard_app
from app.database.db import init_db


def run_dashboard() -> None:
    app = create_dashboard_app()
    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=settings.dashboard_debug,
        use_reloader=False,
    )


def run_bot() -> None:
    from app.bot.discord_bot import run_discord_bot

    run_discord_bot()


def main() -> None:
    init_db()

    if settings.run_mode == "dashboard":
        run_dashboard()
        return

    if settings.run_mode == "bot":
        run_bot()
        return

    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    run_bot()


if __name__ == "__main__":
    main()
