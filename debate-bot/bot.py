"""
bot.py — Telegram Debate Bot main entry point.

Uses python-telegram-bot v20+ (async).
Security: only responds to whitelisted TELEGRAM_CHAT_ID.
"""

import logging
import os
from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from scraper import get_random_post
from debater import get_opening_argument, get_reply, get_summary

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_CHAT_ID = int(os.environ["YOUR_CHAT_ID"])

# ---------------------------------------------------------------------------
# Session state
# In-memory: { chat_id: { "post": {...}, "history": [...] } }
# ---------------------------------------------------------------------------
sessions: dict[int, dict] = {}


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------
def _is_authorised(update: Update) -> bool:
    return update.effective_chat.id == ALLOWED_CHAT_ID


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorised(update):
        return
    await update.message.reply_text(
        "👋 *Debate Bot* — your personal intellectual sparring partner.\n\n"
        "I'll pick a random post from your blog and argue *against* it. "
        "Your job: defend your ideas.\n\n"
        "Commands:\n"
        "  /debate — start a new debate\n"
        "  /end    — end current debate + summary\n"
        "  /help   — show this message",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorised(update):
        return
    await update.message.reply_text(
        "*Commands*\n"
        "  /debate — pick a random blog post and start debating\n"
        "  /end    — end the current debate and get a summary\n"
        "  /help   — show this help\n\n"
        "During a debate, just send any message to continue the argument.",
        parse_mode="Markdown",
    )


async def cmd_debate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorised(update):
        return

    chat_id = update.effective_chat.id

    await update.message.reply_text("Picking a post from your blog...")
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    post = get_random_post()
    if not post:
        await update.message.reply_text(
            "Couldn't fetch your blog right now. "
            "Check that the RSS feed is reachable and try again."
        )
        return

    await update.message.reply_text(
        f"*Post chosen:* [{post['title']}]({post['url']})\n\n"
        "Let's debate. Here's my opening challenge...",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        opening, history = get_opening_argument(post)
    except Exception as exc:
        logger.exception("Gemini error during opening argument")
        await update.message.reply_text(
            f"Gemini hiccuped: {exc}\n\nTry /debate again."
        )
        return

    sessions[chat_id] = {"post": post, "history": history}

    await update.message.reply_text(opening)


async def cmd_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorised(update):
        return

    chat_id = update.effective_chat.id
    session = sessions.pop(chat_id, None)

    if not session:
        await update.message.reply_text("No active debate. Use /debate to start one.")
        return

    await update.message.reply_text("Wrapping up...")
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        summary = get_summary(session["history"])
    except Exception as exc:
        logger.exception("Gemini error during summary")
        summary = "(Could not generate summary due to an error.)"

    await update.message.reply_text(
        f"*Debate over.*\n\n{summary}",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# Message handler (debate turns)
# ---------------------------------------------------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorised(update):
        return

    chat_id = update.effective_chat.id
    session = sessions.get(chat_id)

    if not session:
        await update.message.reply_text(
            "No active debate. Use /debate to pick a post and start one."
        )
        return

    user_text = update.message.text.strip()
    if not user_text:
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        reply, updated_history = get_reply(
            session["post"], session["history"], user_text
        )
        sessions[chat_id]["history"] = updated_history
    except Exception as exc:
        logger.exception("Gemini error during debate reply")
        await update.message.reply_text(
            f"Gemini stumbled: {exc}\n\nYour debate session is still active — try again."
        )
        return

    await update.message.reply_text(reply)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("debate", cmd_debate))
    app.add_handler(CommandHandler("end", cmd_end))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot starting. Authorised chat ID: %d", ALLOWED_CHAT_ID)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
