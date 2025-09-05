"""Miscellaneous utility functions."""

import time


def convert_to_readable_time(seconds: int) -> str:
    """Convert seconds to a human-readable time format (hh:mm:ss or mm:ss).

    Args:
        seconds (int): The number of seconds to convert.

    Returns:
        str: The time in hh:mm:ss format if >= 1 hour, otherwise mm:ss format.

    """
    if seconds >= 3600:
        return time.strftime("%H:%M:%S", time.gmtime(seconds))
    return time.strftime("%M:%S", time.gmtime(seconds))


def parse_youtube_video_id(url: str) -> str:
    """Attempt to extract the Youtube video ID from a URL or return the ID if given directly.

    Args:
        url: The Youtube video URL or ID.

    Returns:
        The extracted video ID.

    """
    if "youtube.com" in url:
        return url.split("?v=")[-1].split("&")[0]

    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    return url
