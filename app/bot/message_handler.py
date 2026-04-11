from __future__ import annotations

from discord import Forbidden, HTTPException, Member, Message

from app.config import settings
from app.database.db import add_violation_points, save_analysis_result
from app.engine.analyzer import analyze_message


async def _delete_message(message: Message) -> bool:
    try:
        await message.delete()
        return True
    except (Forbidden, HTTPException):
        return False


async def _send_warning(message: Message, text: str) -> None:
    try:
        await message.channel.send(f"{message.author.mention} {text}")
    except Exception:
        pass


async def _kick_member(member: Member, reason: str) -> bool:
    try:
        await member.kick(reason=reason)
        return True
    except (Forbidden, HTTPException):
        return False


async def handle_incoming_message(message: Message) -> None:
    if message.author.bot:
        return

    result = analyze_message(message.content)
    label = str(result["label"])

    action_steps: list[str] = []
    message_deleted = False
    user_kicked = False
    violation_points_added = 0
    total_violation_points = 0

    if label == "Aman":
        pass

    elif label == "Waspada":
        message_deleted = await _delete_message(message)
        action_steps.append("delete" if message_deleted else "delete_failed")

        await _send_warning(
            message,
            "peringatan toxic: pesan dihapus karena mengandung kata tidak pantas.",
        )
        action_steps.append("warn")

    elif label == "Indikasi Bullying":
        message_deleted = await _delete_message(message)
        action_steps.append("delete" if message_deleted else "delete_failed")

        await _send_warning(
            message,
            "peringatan: pesan dihapus karena terindikasi cyberbullying. Pelanggaran +1.",
        )
        action_steps.append("warn")

        violation_points_added = 1
        total_violation_points = add_violation_points(
            user_id=str(message.author.id),
            user_name=str(message.author),
            points=violation_points_added,
        )
        action_steps.append("pelanggaran+1")

    elif label == "Indikasi Bullying Berat":
        message_deleted = await _delete_message(message)
        action_steps.append("delete" if message_deleted else "delete_failed")

        await _send_warning(
            message,
            "peringatan keras: pesan dihapus karena terindikasi cyberbullying berat. Pelanggaran +3.",
        )
        action_steps.append("warn")

        violation_points_added = 3
        total_violation_points = add_violation_points(
            user_id=str(message.author.id),
            user_name=str(message.author),
            points=violation_points_added,
        )
        action_steps.append("pelanggaran+3")

    if (
        label in {"Indikasi Bullying", "Indikasi Bullying Berat"}
        and message.guild
        and isinstance(message.author, Member)
        and total_violation_points >= settings.kick_violation_threshold
    ):
        user_kicked = await _kick_member(
            message.author,
            reason=f"Auto moderation: total pelanggaran {total_violation_points}",
        )
        action_steps.append("kick" if user_kicked else "kick_failed")

        if user_kicked:
            try:
                await message.channel.send(
                    f"{message.author.mention} telah dikeluarkan dari server karena total pelanggaran mencapai {total_violation_points}."
                )
            except Exception:
                pass

    save_analysis_result(
        raw_content=message.content,
        normalized_content=result["normalized_text"],
        symbols=" ".join(result["symbols"]),
        trace=" -> ".join(result["trace"]),
        final_state=result["final_state"],
        label=label,
        matched_keywords=", ".join(result["matched_keywords"]),
        user_id=str(message.author.id),
        user_name=str(message.author),
        channel_id=str(message.channel.id),
        channel_name=getattr(message.channel, "name", str(message.channel.id)),
        guild_id=str(message.guild.id) if message.guild else "",
        guild_name=message.guild.name if message.guild else "DM",
        violation_points_added=violation_points_added,
        total_violation_points=total_violation_points,
        action_taken=", ".join(action_steps) if action_steps else "none",
        message_deleted=message_deleted,
        user_kicked=user_kicked,
    )
