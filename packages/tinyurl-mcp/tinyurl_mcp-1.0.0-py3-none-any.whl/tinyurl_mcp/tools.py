from loguru import logger

from tinyurl_mcp.server import mcp
from tinyurl_mcp.models import (
    ApiErrorResponse,
    CreateShortUrlRequest,
    CreateShortUrlResponse,
    UpdateLongUrlRequest,
    UpdateLongUrlResponse,
    DeleteLongUrlRequest,
    DeleteLongUrlResponse,
    ListShortUrlsRequest,
    ListShortUrlsResponse,
)
from tinyurl_mcp.utils import make_api_request, RequestMethod


@mcp.tool()
async def generate_short_url(
    req_data: CreateShortUrlRequest,
) -> CreateShortUrlResponse | ApiErrorResponse:
    """
    Generate a short URL for a given long URL.

    Args:
        req_data: The long URL to shorten along with additional optional parameters.

    Returns:
        A short URL for the given long URL if success else error code along with the message.
    """

    logger.info("Making an API request to generate a new short URL...")
    api_response = await make_api_request(
        api_path="create", req_data=req_data.model_dump_json(exclude_none=True)
    )

    if api_response["code"] == 0:
        return CreateShortUrlResponse(**api_response["data"])
    else:
        return ApiErrorResponse(**api_response)


@mcp.tool()
async def update_long_url(
    req_data: UpdateLongUrlRequest,
) -> UpdateLongUrlResponse | ApiErrorResponse:
    """
    Update long URL associated to an existing short URL.

    Args:
        req_data: The new long URL to associate with the existing short URL.

    Returns:
        The new long URL associated to the existing short URL if success else error code along with the message.
    """

    logger.info("Making an API request to update long URL for an existing short URL...")
    api_response = await make_api_request(
        api_path="change", req_method=RequestMethod.PATCH, req_data=req_data.model_dump_json()
    )

    if api_response["code"] == 0:
        return UpdateLongUrlResponse(**api_response["data"])
    else:
        return ApiErrorResponse(**api_response)


@mcp.tool()
async def delete_short_url(
    req_data: DeleteLongUrlRequest,
) -> DeleteLongUrlResponse | ApiErrorResponse:
    """
    Delete an existing short URL.

    Args:
        req_data: The existing short URL to delete.

    Returns:
        The deleted short URL along with the metadata if success else error code along with the message.
    """

    logger.info("Making an API request to delete an existing short URL...")
    api_response = await make_api_request(
        api_path=f"alias/{req_data.domain}/{req_data.alias}",
        req_method=RequestMethod.DELETE,
    )

    if api_response["code"] == 0:
        return DeleteLongUrlResponse(**api_response["data"])
    else:
        return ApiErrorResponse(**api_response)


@mcp.tool()
async def list_short_urls(
    req_data: ListShortUrlsRequest,
) -> ListShortUrlsResponse | ApiErrorResponse:
    """
    List all the existing available or archived short URLs.

    Args:
        req_data: Parameters to filter the listed short URLs.

    Returns:
        The list of short URLs along with the metadata if success else error code along with the message.
    """

    logger.info("Making an API request to list all the existing short URLs...")
    api_response = await make_api_request(
        api_path=f"urls/{req_data.type}",
        req_method=RequestMethod.GET,
        query_params=req_data.model_dump_json(exclude_none=True, exclude={"type"}),
    )

    if api_response["code"] == 0:
        return ListShortUrlsResponse(urls=api_response["data"])
    else:
        return ApiErrorResponse(**api_response)
