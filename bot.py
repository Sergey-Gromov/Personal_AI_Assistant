"""
Main Bot Module.
Initializes and configures the Telegram bot using pyTelegramBotAPI.
"""

import types
from urllib.parse import urlparse

import aiohttp
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_helper

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY_URL, TELEGRAM_REQUEST_TIMEOUT
from utils.logging import logger


def _is_socks_proxy(proxy_url: str) -> bool:
    """Return True when proxy URL uses SOCKS protocol."""
    scheme = urlparse(proxy_url).scheme.lower()
    return scheme in {"socks4", "socks4a", "socks5", "socks5h"}


def _configure_socks_proxy(proxy_url: str) -> None:
    """Configure telebot aiohttp session manager to use SOCKS proxy connector."""
    try:
        from aiohttp_socks import ProxyConnector
    except ImportError as exc:
        raise RuntimeError(
            "SOCKS proxy requires package 'aiohttp-socks'. Install dependencies from requirements.txt"
        ) from exc

    session_manager = asyncio_helper.session_manager
    request_limit = asyncio_helper.REQUEST_LIMIT

    async def _create_session_with_proxy(self):
        connector = ProxyConnector.from_url(
            proxy_url,
            limit=request_limit,
            ssl=self.ssl_context,
        )
        self.session = aiohttp.ClientSession(connector=connector)
        return self.session

    session_manager.create_session = types.MethodType(
        _create_session_with_proxy,
        session_manager,
    )
    # Per-request proxy is not needed with ProxyConnector.
    asyncio_helper.proxy = None


# Configure Telegram API transport (proxy and timeout)
if TELEGRAM_PROXY_URL:
    if _is_socks_proxy(TELEGRAM_PROXY_URL):
        _configure_socks_proxy(TELEGRAM_PROXY_URL)
        logger.info("Telegram SOCKS proxy enabled")
    else:
        asyncio_helper.proxy = TELEGRAM_PROXY_URL
        logger.info("Telegram HTTP proxy enabled")

asyncio_helper.REQUEST_TIMEOUT = TELEGRAM_REQUEST_TIMEOUT
logger.info(f"Telegram request timeout: {TELEGRAM_REQUEST_TIMEOUT}s")

# Create bot instance
bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN, parse_mode='Markdown')

logger.info("Bot instance created")
