from __future__ import annotations

from flask import Flask


def register_filters(app: Flask) -> None:
    @app.template_filter("label_badge_class")
    def label_badge_class(label: str) -> str:
        mapping = {
            "Aman": "badge badge-safe",
            "Waspada": "badge badge-warn",
            "Indikasi Bullying": "badge badge-danger",
            "Indikasi Bullying Berat": "badge badge-danger-strong",
        }
        return mapping.get(label, "badge")

    @app.template_filter("action_parts")
    def action_parts(action_taken: str) -> list[str]:
        if not action_taken or action_taken == "none":
            return []
        return [part.strip() for part in action_taken.split(",") if part.strip()]

    @app.template_filter("action_badge_class")
    def action_badge_class(action: str) -> str:
        if action.startswith("delete"):
            return "badge badge-neutral"
        if action.startswith("warn"):
            return "badge badge-warn"
        if action.startswith("pelanggaran+"):
            return "badge badge-danger"
        if action.startswith("kick"):
            return "badge badge-danger-strong"
        return "badge badge-neutral"

    @app.template_filter("action_label")
    def action_label(action: str) -> str:
        mapping = {
            "delete": "Hapus",
            "delete_failed": "Hapus Gagal",
            "warn": "Peringatan",
            "kick": "Kick",
            "kick_failed": "Kick Gagal",
            "pelanggaran+1": "+1 Pelanggaran",
            "pelanggaran+3": "+3 Pelanggaran",
        }
        return mapping.get(action, action)
