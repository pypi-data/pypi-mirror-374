"""Fetch transcript."""

import asyncio
from typing import Iterable

from requests import Session
from youtube_transcript_api import FetchedTranscript, YouTubeTranscriptApi
from youtube_transcript_api.proxies import ProxyConfig

from yt_summary.extractors.metadata import extract_metadata
from yt_summary.schemas.models import YoutubeTranscriptRaw
from yt_summary.utils.async_helpers import to_async
from yt_summary.utils.misc import convert_to_readable_time, parse_youtube_video_id


class TranscriptExtractor:
    """Transcript extractor. A wrapper around YouTubeTranscriptApi.

    Attributes:
        ytt_api: YouTubeTranscriptApi instance

    """

    def __init__(self, proxy_config: ProxyConfig | None = None, http_client: Session | None = None) -> None:
        self.ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config, http_client=http_client)

    async def fetch(
        self, url: str, languages: Iterable[str] | None = None, *, preserve_formatting: bool = False
    ) -> YoutubeTranscriptRaw:
        """Asynchronously fetch transcript.

        Args:
            url: video URL or ID you want to retrieve the transcript for.
            languages: A list of language codes in a descending priority. For
                example, if this is set to ["de", "en"] it will first try to fetch the
                german transcript (de) and then fetch the english transcript (en) if
                it fails to do so. This defaults to ["en"].
            sentences_per_timestamp_group: number of sentences to stitch together. To
                improve granularity, reduce this number.
            preserve_formatting: whether to keep select HTML text formatting

        Returns:
            The transcript text.

        """
        fetched_transcript, metadata = await asyncio.gather(
            self._afetch_transcript(
                url,
                languages=languages,
                preserve_formatting=preserve_formatting,
            ),
            extract_metadata(url),
        )
        text = " ".join([f"[{convert_to_readable_time(int(s.start))}] {s.text}" for s in fetched_transcript.snippets])
        metadata.is_generated = fetched_transcript.is_generated
        metadata.language = fetched_transcript.language
        metadata.language_code = fetched_transcript.language_code
        return YoutubeTranscriptRaw(
            metadata=metadata,
            text=text,
        )

    def fetch_transcript(
        self, url: str, languages: Iterable[str] | None = None, *, preserve_formatting: bool = False
    ) -> FetchedTranscript:
        """Fetch transcript.

        Args:
            url: video URL or ID you want to retrieve the transcript for.
            languages: A list of language codes in a descending priority. For
                example, if this is set to ["de", "en"] it will first try to fetch the
                german transcript (de) and then fetch the english transcript (en) if
                it fails to do so. This defaults to ["en"].
            preserve_formatting: whether to keep select HTML text formatting

        Returns:
            The transcript text.

        """
        video_id = parse_youtube_video_id(url)
        return self.ytt_api.fetch(
            video_id,
            languages=languages if languages else ["en"],
            preserve_formatting=preserve_formatting,
        )

    async def _afetch_transcript(
        self, url: str, languages: Iterable[str] | None = None, *, preserve_formatting: bool = False
    ) -> FetchedTranscript:
        """Asynchronously fetch transcript.

        Args:
            url: video URL or ID you want to retrieve the transcript for.
            languages: A list of language codes in a descending priority. For
                example, if this is set to ["de", "en"] it will first try to fetch the
                german transcript (de) and then fetch the english transcript (en) if
                it fails to do so. This defaults to ["en"].
            preserve_formatting: whether to keep select HTML text formatting

        Returns:
            The transcript text.

        """
        kwargs = {
            "url": url,
            "languages": languages,
            "preserve_formatting": preserve_formatting,
        }
        return await to_async(self.fetch_transcript, **kwargs)
