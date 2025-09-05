"""Response models for summarisers."""

from pydantic import BaseModel


class TimestampResponse(BaseModel):
    """Response model for timestamped summary.

    Attributes:
        timestamp: Timestamp in seconds.
        text: Summary text.

    """

    timestamp: int
    text: str


class TimestampSummary(BaseModel):
    """Response model for timestamped summary.

    Attributes:
        summary: Overall summary of the transcript.
        responses: List of timestamped summary points.

    """

    summary: str
    repsonses: list[TimestampResponse]
