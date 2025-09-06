import os
import httpx
import dateparser

from datetime import datetime
from enum import Enum
from loguru import logger
from typing import Any, Optional


class RequestMethod(str, Enum):
    """Enum for HTTP request methods."""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"


async def make_api_request(
    api_path: str,
    req_method: RequestMethod,
    req_data: Optional[dict[str, Any]] = None,
    query_params: Optional[dict[str, Any]] = None,
) -> dict[str, Any] | None:
    """Make a request to the TinyURL API with proper error handling."""

    # check for the API key
    api_key = os.environ.get("TINY_URL_API_KEY", None)
    if not api_key:
        err_msg = "TinyURL API key not found in environment variables."
        logger.error(err_msg)
        raise KeyError(err_msg)

    url = f"https://api.tinyurl.com/{api_path}"

    headers = {
        "User-Agent": "VimalPaliwal TinyURL MCP",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # make async request to the api server
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"API URL: {url}")
            logger.info(f"Request data: {req_data}")
            logger.info(f"Query Params: {query_params}")

            request = httpx.Request(
                req_method.value, url, headers=headers, data=req_data, params=query_params
            )
            response = await client.send(request)

            logger.info(f"Response: {response.status_code} - {response.json()}")

            return response.json()
        except Exception:
            logger.exception("TinyURL API request failed.")
            raise


def date_parser_absolute(valid_until: str) -> str:
    """
    Validate and parse a given date string. The date string can be either relative or absolute.

    Args:
        valid_until: The date string to validate and parse.

    Returns:
        The parsed date in ISO8601 format YYYY-MM-DD HH:MM:SS.
    """
    # Parse the date
    parsed_date = dateparser.parse(valid_until)

    # check if parsed_date is None
    if parsed_date is None:
        err_msg = f"Error: Failed to parse the date {valid_until}. Please provide a valid date."
        logger.error(err_msg)
        raise ValueError(err_msg)

    # check if date is in the past
    if parsed_date.date() < datetime.now().date():
        err_msg = f"Error: {valid_until} is in the past. Please provide a future date."
        logger.error(err_msg)
        raise ValueError(err_msg)

    return parsed_date.isoformat(sep=" ", timespec="seconds")
