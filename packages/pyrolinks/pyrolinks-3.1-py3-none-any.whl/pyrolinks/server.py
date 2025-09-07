import asyncio
import ssl
import contextlib
import logging
from typing import Optional
from aiohttp import web, ClientConnectionError
from pyrogram.errors import OffsetInvalid
from .utils import content_disposition, parse_range
from .errors import InvalidParameterError, FileStreamError, ServerError

CHUNK_SIZE = 1024 * 1024  # Pyrogram streams chunks of up to 1 MiB

logger = logging.getLogger(__name__)  # Server logger


def create_ssl_context(cert_path: Optional[str], key_path: Optional[str]) -> Optional[ssl.SSLContext]:
    """
    Create SSL context for HTTPS if both certificate and key are provided.
    Returns None for HTTP.
    """
    if not cert_path and not key_path:
        return None
    if not cert_path or not key_path:
        raise ServerError("Both ssl_cert and ssl_key must be provided for HTTPS")
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)
    return ctx


def create_app(pyro_client, route: str = "/dl") -> web.Application:
    """
    Create an aiohttp application with a GET endpoint for streaming Telegram files.
    Supports HTTP Range requests and handles OffsetInvalid errors safely.
    """
    app = web.Application()

    async def download_handler(request: web.Request) -> web.StreamResponse:
        """
        Handle GET requests for file streaming.
        Implements:
        - Range header parsing
        - Chunk-based streaming (1 MiB chunks)
        - Fallback to streaming from offset=0 if Pyrogram raises OffsetInvalid
        """

        file_id = request.query.get("file_id")
        size_str = request.query.get("size")
        name = request.query.get("name", "file")
        mime = request.query.get("mime", "application/octet-stream")

        # Validate required query parameters
        try:
            if not file_id or not size_str:
                raise InvalidParameterError("Missing required query params: file_id and size")
            total_size = int(size_str)
            if total_size <= 0:
                raise InvalidParameterError("Invalid 'size' parameter")
        except ValueError:
            raise InvalidParameterError("Invalid 'size' parameter (not an integer)")

        # Parse Range header if present
        byte_range = parse_range(request.headers.get("Range"), total_size)
        if byte_range:
            start_byte, end_byte = byte_range
            status_code = 206  # Partial Content
            content_length = end_byte - start_byte + 1
        else:
            start_byte, end_byte = 0, total_size - 1
            status_code = 200
            content_length = total_size

        if start_byte >= total_size:
            return web.Response(
                status=416,
                headers={"Content-Range": f"bytes */{total_size}", "Accept-Ranges": "bytes"}
            )

        headers = {
            "Accept-Ranges": "bytes",
            "Content-Type": mime,
            "Content-Disposition": content_disposition(name),
            "Content-Length": str(content_length),
            "Access-Control-Allow-Origin": "*",
        }
        if status_code == 206:
            headers["Content-Range"] = f"bytes {start_byte}-{end_byte}/{total_size}"

        resp = web.StreamResponse(status=status_code, headers=headers)
        await resp.prepare(request)

        bytes_remaining = content_length
        chunk_index = start_byte // CHUNK_SIZE
        skip_in_chunk = start_byte - (chunk_index * CHUNK_SIZE)

        logger.debug(f"Streaming file {file_id} from {start_byte} to {end_byte}, total={total_size}, "
                     f"chunk_index={chunk_index}, skip_in_chunk={skip_in_chunk}")

        try:
            async for chunk in pyro_client.stream_media(file_id, offset=chunk_index):
                if not chunk:
                    break

                if skip_in_chunk:
                    if len(chunk) <= skip_in_chunk:
                        skip_in_chunk -= len(chunk)
                        continue
                    chunk = chunk[skip_in_chunk:]
                    skip_in_chunk = 0

                if len(chunk) > bytes_remaining:
                    chunk = chunk[:bytes_remaining]

                try:
                    await resp.write(chunk)
                except (ClientConnectionError, ConnectionResetError, RuntimeError):
                    logger.info("Client disconnected during streaming")
                    return resp

                bytes_remaining -= len(chunk)
                if bytes_remaining <= 0:
                    return resp

            return resp

        except OffsetInvalid:
            logger.warning("OffsetInvalid detected, falling back to streaming from offset=0")
            try:
                bytes_skipped = 0
                async for chunk in pyro_client.stream_media(file_id, offset=0):
                    if not chunk:
                        break

                    if bytes_skipped + len(chunk) <= start_byte:
                        bytes_skipped += len(chunk)
                        continue

                    if bytes_skipped < start_byte:
                        chunk = chunk[start_byte - bytes_skipped:]
                        bytes_skipped = start_byte

                    if len(chunk) > bytes_remaining:
                        chunk = chunk[:bytes_remaining]

                    try:
                        await resp.write(chunk)
                    except (ClientConnectionError, ConnectionResetError, RuntimeError):
                        logger.info("Client disconnected during fallback streaming")
                        return resp

                    bytes_remaining -= len(chunk)
                    if bytes_remaining <= 0:
                        return resp

                return resp

            except Exception as e:
                with contextlib.suppress(Exception):
                    if resp.prepared:
                        await resp.write_eof()
                raise FileStreamError(f"Streaming error during fallback: {e}") from e

        except (ClientConnectionError, ConnectionResetError, asyncio.CancelledError, RuntimeError) as conn_error:
            logger.info("Client disconnected during streaming: %s", type(conn_error).__name__)
            return resp
        except Exception as e:
            with contextlib.suppress(Exception):
                if resp.prepared:
                    await resp.write_eof()
            raise FileStreamError(f"Streaming error: {e}") from e

    app.router.add_get(route, download_handler)
    return app


async def run_server(
    pyro_client,
    host: str = "0.0.0.0",
    port: int = 8080,
    route: str = "/dl",
    ssl_cert: Optional[str] = None,
    ssl_key: Optional[str] = None
):
    """
    Setup and start aiohttp server with optional HTTPS.
    Returns runner and site objects.
    """
    try:
        app = create_app(pyro_client, route=route)
        runner = web.AppRunner(app)
        await runner.setup()
        ssl_ctx = create_ssl_context(ssl_cert, ssl_key)
        site = web.TCPSite(runner, host=host, port=port, ssl_context=ssl_ctx)
        await site.start()
        logger.info(f"Server started on {host}:{port}{route}")
        return runner, site
    except Exception as e:
        raise ServerError(f"Failed to start HTTP server: {e}") from e