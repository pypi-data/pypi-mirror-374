"""Utility functions for type conversions and environment variable handling."""

import asyncio
import os
import threading

from a2a.types import FilePart, FileWithBytes, Part, TextPart
from google.genai import types

from aigency.utils.logger import get_logger

logger = get_logger()


def convert_a2a_part_to_genai(part: Part) -> types.Part:
    """Convert a single A2A Part type into a Google Gen AI Part type.

    Args:
        part (Part): The A2A Part to convert.

    Returns:
        types.Part: The equivalent Google Gen AI Part.

    Raises:
        ValueError: If the part type is not supported.
    """
    part = part.root
    if isinstance(part, TextPart):
        return types.Part(text=part.text)
    raise ValueError(f"Unsupported part type: {type(part)}")


def convert_genai_part_to_a2a(part: types.Part) -> Part:
    """Convert a single Google Gen AI Part type into an A2A Part type.

    Args:
        part (types.Part): The Google Gen AI Part to convert.

    Returns:
        Part: The equivalent A2A Part.

    Raises:
        ValueError: If the part type is not supported.
    """
    if part.text:
        return TextPart(text=part.text)
    if part.inline_data:
        return Part(
            root=FilePart(
                file=FileWithBytes(
                    bytes=part.inline_data.data,
                    mime_type=part.inline_data.mime_type,
                )
            )
        )
    raise ValueError(f"Unsupported part type: {part}")


def expand_env_vars(env_dict):
    """
    Expande los valores del diccionario usando variables de entorno solo si el valor es una clave de entorno existente.
    Si la variable no existe en el entorno, deja el valor literal.
    """
    result = {}
    for k, v in env_dict.items():
        if isinstance(v, str) and v in os.environ:
            result[k] = os.getenv(v)
        else:
            logger.warning(f"Environment variable {v} not found")
    return result


def generate_url(host: str, port: int, path: str = "") -> str:
    """Generate a URL from host, port, and path components.

    Args:
        host (str): Hostname or IP address.
        port (int): Port number.
        path (str, optional): URL path. Defaults to "".

    Returns:
        str: Complete URL in the format http://host:port/path.
    """
    return f"http://{host}:{port}{path}"


def safe_async_run(coro):
    """Simple wrapper to safely run async code."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():

            result = None
            exception = None

            def run_in_thread():
                nonlocal result, exception
                try:
                    result = asyncio.run(coro)
                except Exception as e:
                    exception = e

            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()

            if exception:
                raise exception
            return result
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

