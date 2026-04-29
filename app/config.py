from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _parse_csv_ints(raw_value: str | None) -> list[int]:
    if not raw_value or not raw_value.strip():
        return []

    result: list[int] = []
    for item in raw_value.split(","):
        item = item.strip()
        if item:
            result.append(int(item))
    return result


def _parse_optional_int(raw_value: str | None) -> int | None:
    if raw_value is None:
        return None
    raw_value = raw_value.strip()
    if not raw_value:
        return None
    return int(raw_value)


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    data_dir: Path
    dictionaries_dir: Path
    discord_bot_token: str
    discord_guild_id: int | None
    discord_allowed_channel_ids: list[int] = field(default_factory=list)
    flask_host: str = "127.0.0.1"
    flask_port: int = 5000
    database_path: Path = BASE_DIR / "app.db"
    run_mode: str = "both"
    dashboard_debug: bool = True
    kick_violation_threshold: int = 3


def load_settings() -> Settings:
    return Settings(
        base_dir=BASE_DIR,
        data_dir=BASE_DIR / "data",
        dictionaries_dir=BASE_DIR / "data" / "dictionaries",
        discord_bot_token=os.getenv("DISCORD_BOT_TOKEN", ""),
        discord_guild_id=_parse_optional_int(os.getenv("DISCORD_GUILD_ID")),
        discord_allowed_channel_ids=_parse_csv_ints(os.getenv("DISCORD_ALLOWED_CHANNEL_IDS", "")),
        flask_host=os.getenv("FLASK_HOST", "127.0.0.1"),
        flask_port=int(os.getenv("FLASK_PORT", "5000")),
        database_path=BASE_DIR / os.getenv("DATABASE_PATH", "app.db"),
        run_mode=os.getenv("RUN_MODE", "both").lower().strip(),
        dashboard_debug=os.getenv("DASHBOARD_DEBUG", "true").lower() == "true",
        kick_violation_threshold=int(os.getenv("KICK_VIOLATION_THRESHOLD", "3")),
    )


settings = load_settings()