from __future__ import annotations

import discord

from app.bot.message_handler import handle_incoming_message
from app.config import settings


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready() -> None:
    bot_user = bot.user.name if bot.user else "unknown"
    print(f"[BOT] Logged in as {bot_user}")


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if settings.discord_guild_id and message.guild and message.guild.id != settings.discord_guild_id:
        return

    if (
        settings.discord_allowed_channel_ids
        and message.channel.id not in settings.discord_allowed_channel_ids
    ):
        return

    await handle_incoming_message(message)


def run_discord_bot() -> None:
    if not settings.discord_bot_token:
        raise RuntimeError("DISCORD_BOT_TOKEN belum diisi di file .env")

    bot.run(settings.discord_bot_token)
