import asyncio
import logging
from pyrogram import Client as PyroClient
from .core import generate_link
from .server import run_server
from .errors import PyroLinksError, ServerError


class PyroLinks:
    def __init__(
        self,
        pyro_client: PyroClient,
        *,
        schema: str = "http",
        domain: str | None = None,
        ip: str = "0.0.0.0",
        port: int = 8080,
        route: str = "/dl",
        ssl_cert: str | None = None,
        ssl_key: str | None = None,
        logger: logging.Logger | None = None,
    ):
        """
        Attach a download server to an existing Pyrogram Client.
        Works similar to pytgcalls design.
        """
        self.bot = pyro_client
        self.schema = schema
        self.domain = domain
        self.ip = ip
        self.port = port
        self.route = route
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key

        self.logger = logger or logging.getLogger("PyroLinks")
        self.runner = None
        self.site = None

    @property
    def base_url(self) -> str:
        host_for_link = self.domain if self.domain else self.ip
        return f"{self.schema}://{host_for_link}:{self.port}{self.route}"

    async def start(self):
        """
        Start the Pyrogram bot (if not already started) and the HTTP server.
        """
        try:
            await self.bot.start()
            self.runner, self.site = await run_server(
                self.bot,
                host=self.ip,
                port=self.port,
                route=self.route,
                ssl_cert=self.ssl_cert,
                ssl_key=self.ssl_key
            )
            self.logger.info("PyroLinks started at %s", self.base_url)
        except Exception as e:
            raise ServerError(f"Failed to start PyroLinks: {e}") from e

    async def stop(self):
        """
        Stop the HTTP server and the Pyrogram bot.
        """
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            await self.bot.stop()
            self.logger.info("PyroLinks stopped.")
        except Exception as e:
            raise ServerError(f"Failed to stop PyroLinks: {e}") from e

    async def generate_link(self, message):
        """
        Generate a direct download link for a given Pyrogram Message.
        """
        try:
            return await generate_link(message, self.base_url)
        except Exception as e:
            raise PyroLinksError(f"Failed to generate link: {e}") from e


def compose(instances: list["PyroLinks"]):
    """
    Start multiple PyroLinks instances together (like pytgcalls.compose).
    Uses the current event loop (avoids 'attached to a different loop' error).
    """
    async def runner():
        for inst in instances:
            await inst.start()
        await asyncio.Event().wait()  # block forever until Ctrl+C

    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner())        self.logger = logging.getLogger("PyrolinksClient")

        if schema not in ("http", "https"):
            raise ValueError("schema must be 'http' or 'https'")

        self.schema = schema
        self.domain = domain
        self.ip = ip or "0.0.0.0"
        self.port = port
        self.route = route
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.bot = PyroClient(**client_kwargs)
        self.runner = None
        self.site = None

    @property
    def base_url(self) -> str:
        host_for_link = self.domain if self.domain else self.ip
        return f"{self.schema}://{host_for_link}:{self.port}{self.route}"

    async def start(self):
        self.logger.info("Starting Pyrolinks client and server...")
        try:
            await self.bot.start()
            self.runner, self.site = await run_server(
                self.bot,
                host=self.ip,
                port=self.port,
                route=self.route,
                ssl_cert=self.ssl_cert,
                ssl_key=self.ssl_key
            )
        except Exception as e:
            raise ServerError(f"Failed to start bot/server: {e}") from e

    async def stop(self):
        self.logger.info("Stopping Pyrolinks client and server...")
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            await self.bot.stop()
        except Exception as e:
            raise ServerError(f"Failed to stop bot/server: {e}") from e

    def on_message(self, *args, **kwargs):
        return self.bot.on_message(*args, **kwargs)

    async def generate_link(self, message):
        try:
            return await generate_link(message, self.base_url)
        except Exception as e:
            raise PyroLinksError(f"Failed to generate link: {e}") from e
