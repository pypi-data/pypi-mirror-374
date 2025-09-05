"""Exceptions raised by yt-summary."""


class YTSummaryExpection(Exception):
    """Base class for all exceptions raised by yt-summary."""


class MetadataNotFoundException(YTSummaryExpection):
    """Raised when no metadata is found for the provided URL or video ID."""

    def __init__(self, aiohttp_client_error: Exception) -> None:
        message = "Failed to fetch the metadata. Http error: \n"
        super().__init__(f"{message}{aiohttp_client_error}")
