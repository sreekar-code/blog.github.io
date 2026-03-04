"""
debater.py — Gemini-powered debate opponent.

Uses google-genai SDK (new, non-deprecated) with gemini-2.0-flash.
Maintains conversation history externally (caller owns history list).
History format: list of {"role": "user"|"model", "parts": ["text"]} dicts.
"""
from __future__ import annotations

import logging
import os

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a ruthless debate opponent. Your only job is to dismantle Sreekar's ideas completely.

Rules — follow them strictly:
1. Be brutal and direct. No softening, no hedging, no "that's a fair point." Go for the throat.
2. Find the weakest assumption in his argument and destroy it first. Don't spread thin — pick the kill shot.
3. Use his own words and logic against him. Quote him, then show why it collapses.
4. Keep it SHORT. 2-4 sentences is ideal. Only go longer if the argument genuinely demands it. Never pad.
5. End every response with ONE sharp question that corners him — something he can't dodge without exposing a flaw.
6. No political correctness. No diplomatic cushioning. Intellectually honest, not polite.
7. Never concede unless his argument is airtight and you have no counter. That should be rare."""

MODEL = "gemini-2.5-flash"

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        _client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialised (model: %s).", MODEL)
    return _client


def _make_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE",
            ),
        ],
    )


def _history_to_contents(history: list[dict]) -> list[types.Content]:
    """Convert our internal history format to SDK Content objects."""
    contents = []
    for turn in history:
        contents.append(
            types.Content(
                role=turn["role"],
                parts=[types.Part(text=p) for p in turn["parts"]],
            )
        )
    return contents


def _build_context_message(post: dict) -> str:
    return (
        f"Here is the blog post we will debate. Read it carefully — "
        f"you will challenge the ideas in it.\n\n"
        f"TITLE: {post['title']}\n"
        f"URL: {post['url']}\n\n"
        f"CONTENT:\n{post['full_text']}"
    )


def get_opening_argument(post: dict) -> tuple[str, list[dict]]:
    """
    Gemini opens the debate by challenging the post's main thesis.

    Returns:
        (response_text, history)
    """
    client = _get_client()

    opening_prompt = (
        _build_context_message(post)
        + "\n\n---\n\n"
        "Now open the debate. Identify the central thesis of this post and challenge it "
        "head-on. Be specific — quote or paraphrase Sreekar's own words if it sharpens "
        "your attack. End with a pointed question that forces him to defend a core assumption."
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=opening_prompt,
        config=_make_config(),
    )
    reply_text = response.text.strip()

    history: list[dict] = [
        {"role": "user", "parts": [opening_prompt]},
        {"role": "model", "parts": [reply_text]},
    ]

    logger.info("Opening argument generated (%d chars).", len(reply_text))
    return reply_text, history


def get_reply(post: dict, history: list[dict], user_message: str) -> tuple[str, list[dict]]:
    """
    Continue the debate given the full conversation history and user's latest message.

    Returns:
        (response_text, updated_history)
    """
    client = _get_client()

    # Build contents: existing history + new user message
    contents = _history_to_contents(history) + [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=_make_config(),
    )
    reply_text = response.text.strip()

    updated_history = history + [
        {"role": "user", "parts": [user_message]},
        {"role": "model", "parts": [reply_text]},
    ]

    logger.info(
        "Debate reply generated (%d chars), history depth=%d.",
        len(reply_text),
        len(updated_history),
    )
    return reply_text, updated_history


def get_summary(history: list[dict]) -> str:
    """Generate a 2-line summary of what was argued in the debate."""
    client = _get_client()

    summary_prompt = (
        "The debate is now over. In exactly 2 short sentences, summarise: "
        "(1) what position Sreekar defended and (2) what the strongest counter-argument raised was. "
        "Be crisp and neutral."
    )

    contents = _history_to_contents(history) + [
        types.Content(role="user", parts=[types.Part(text=summary_prompt)])
    ]

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=_make_config(),
    )
    return response.text.strip()


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    sample_post = {
        "title": "Why I Think Most Productivity Advice Is Wrong",
        "url": "https://sreekarscribbles.com/sample",
        "full_text": (
            "Most productivity advice focuses on doing more things faster. "
            "But I believe the real problem is that people are doing the wrong things at high speed. "
            "A calendar full of meetings is not productivity — it's theatre. "
            "True productivity is ruthless prioritisation: saying no to almost everything "
            "so you can say a deep yes to the one thing that matters most today."
        ),
    }

    print("=== Testing get_opening_argument ===")
    opening, hist = get_opening_argument(sample_post)
    print(f"Opening:\n{opening}\n")

    print("=== Testing get_reply ===")
    reply, hist = get_reply(
        sample_post,
        hist,
        "But deep focus only works if you pick the right thing to focus on — that's the hard part.",
    )
    print(f"Reply:\n{reply}\n")

    print("=== Testing get_summary ===")
    summary = get_summary(hist)
    print(f"Summary:\n{summary}")
