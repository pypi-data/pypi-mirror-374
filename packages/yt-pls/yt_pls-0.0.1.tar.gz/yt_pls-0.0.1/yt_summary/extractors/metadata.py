"""Extract metadata from YouTube videos using yt-dlp."""

import aiohttp
from pydantic import HttpUrl

from yt_summary.schemas.exceptions import MetadataNotFoundException
from yt_summary.schemas.models import YoutubeMetadata
from yt_summary.utils.misc import parse_youtube_video_id


async def extract_metadata(url: str) -> YoutubeMetadata:
    """Extract metadata from a YouTube video URL.

    Args:
        url: The YouTube video URL.

    Returns:
        A tuple containing the YoutubeMetadata object and subtitles dictionary (if available).

    Raises:
        MetadataNotFoundError: If there is an error fetching the metadata.

    """
    if "youtube.com" not in url and "youtu.be" not in url:
        url = f"https://www.youtube.com/watch?v={url}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://www.youtube.com/oembed?url={url}&format=json",
                headers={"Accept": "application/json"},
                raise_for_status=True,
            ) as response:
                metadata = await response.json()
    except aiohttp.ClientError as e:
        raise MetadataNotFoundException(e) from e

    return YoutubeMetadata(
        video_id=parse_youtube_video_id(url),
        title=metadata["title"],
        author=metadata["author_name"],
        channel_id=metadata["author_url"].split("@")[-1],
        video_url=HttpUrl(url.split("&")[0]),
        channel_url=HttpUrl(metadata["author_url"]),
        thumbnail_url=HttpUrl(metadata.get("thumbnail_url")),
    )
