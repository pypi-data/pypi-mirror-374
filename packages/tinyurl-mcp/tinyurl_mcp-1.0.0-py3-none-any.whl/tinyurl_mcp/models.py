from pydantic import BaseModel, Field, HttpUrl, PositiveInt, ConfigDict, field_serializer
from typing import Optional, Literal

from tinyurl_mcp.utils import date_parser_absolute


class ApiErrorResponse(BaseModel):
    """
    Response schema for failed API responses.
    """

    code: PositiveInt = Field(
        description="Operation result code. 0 means success, anything else means failure",
    )
    errors: list[str] = Field(description="List of errors that occurred")

    # ignore additional arguments
    model_config = ConfigDict(extra="ignore")


class CreateShortUrlRequest(BaseModel):
    """
    Request schema for creating a new short URL.
    """

    url: HttpUrl = Field(description="The long URL that will be shortened")
    domain: Optional[str] = Field(
        default="tinyurl.com", description="The domain you would like the TinyURL to use"
    )
    alias: Optional[str] = Field(
        default=None,
        description="A short string of characters to use in the TinyURL. If ommitted, one will be randomly generated. When using a branded domain, this has a minimum length of 1 character",
        min_length=1,
        max_length=30,
    )
    tags: Optional[str] = Field(
        default=None,
        description="A comma-separated list of tags to apply to the TinyURL. Tags group and categorize TinyURLs together",
        max_length=45,
    )
    expires_at: Optional[str] = Field(
        default=None,
        description="TinyURL expiration in ISO8601 format. Set to null so TinyURL never expires. Example: 2024-10-25 10:11:12",
    )
    description: Optional[str] = Field(
        default=None,
        description="The alias description",
        min_length=3,
        max_length=1000,
    )

    @field_serializer("expires_at")
    def serialize_expires_at(self, expires_at: str):
        return date_parser_absolute(expires_at)


class CreateShortUrlResponse(BaseModel):
    """
    Response schema for creating a new short URL.
    """

    tiny_url: str = Field(description="The shortened URL")
    expires_at: str = Field(
        description="TinyURL expiration in ISO8601 format. Example: 2024-10-25 10:11:12",
    )


class UpdateLongUrlRequest(BaseModel):
    """
    Request schema to update a long URL for an exisiting short URL.
    """

    url: HttpUrl = Field(description="The long URL that will be shortened")
    domain: Optional[str] = Field(
        default="tinyurl.com", description="The custom domain used for the short URL"
    )
    alias: str = Field(
        description="The existing alias for the short URL",
        min_length=1,
        max_length=30,
    )


class UpdateLongUrlResponse(BaseModel):
    """
    Response schema to update a long URL for an exisiting short URL.
    """

    url: str = Field(description="The long URL")


class DeleteLongUrlRequest(BaseModel):
    """
    Request schema to delete an exisiting short URL
    """

    domain: Optional[str] = Field(
        default="tinyurl.com", description="The custom domain used for the short URL"
    )
    alias: str = Field(
        description="The existing alias for the short URL",
        min_length=1,
        max_length=30,
    )


class DeleteLongUrlResponse(BaseModel):
    """
    Response schema to delete an exisiting short URL.
    """

    tiny_url: str = Field(description="The short URL")
    url: str = Field(description="The long URL")
    deleted: bool = Field(description="Whether the short URL was deleted")
    archived: bool = Field(description="Whether the short URL was archived")


class ListShortUrlsRequest(BaseModel):
    """
    Request schema to list all the existing available or archived short URLs.
    """

    type: Optional[Literal["available", "archived"]] = Field(
        default="available", description="Whether to list all the available or archived short URLs"
    )
    from_date: Optional[str] = Field(
        default=None,
        description="Only list short URLs created on and after this date. Date must be in ISO8601 format. Example: 2024-10-25 10:11:12",
    )
    to_date: Optional[str] = Field(
        default=None,
        description="Only list short URLs created until this date. Date must be in ISO8601 format. Example: 2024-10-25 10:11:12",
    )
    search: Optional[str] = Field(
        default=None,
        description="Only list short URLs that match this search string. Prefix either alias or tag keyword followed by a colon to the search term. Eg. tag:organisation",
    )

    @field_serializer("from_date")
    def serialize_from_date(self, from_date: str):
        return date_parser_absolute(from_date)

    @field_serializer("to_date")
    def serialize_to_date(self, to_date: str):
        return date_parser_absolute(to_date)


class ListShortUrlResponse(BaseModel):
    """
    Response schema to list the existing available or archived short URL.
    """

    tiny_url: str = Field(description="The short URL")
    deleted: bool = Field(description="Whether the short URL was deleted")
    archived: bool = Field(description="Whether the short URL was archived")
    created_at: str = Field(
        description="Short URL creation in ISO8601 format. Example: 2024-10-25 10:11:12",
    )
    expires_at: Optional[str] = Field(
        default=None,
        description="Short URL expiration in ISO8601 format. Example: 2024-10-25 10:11:12",
    )
    tags: list[str] = Field(description="List of tags applied to the short URL")


class ListShortUrlsResponse(BaseModel):
    """
    Response schema to list all the existing available or archived short URL.
    """

    urls: list[ListShortUrlResponse] = Field(description="List of short URLs")
