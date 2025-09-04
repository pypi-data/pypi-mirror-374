"""Runner functions to simplify usage of the package."""

from requests import Session
from youtube_transcript_api.proxies import ProxyConfig

from yt_summary.extractors.transcript import TranscriptExtractor
from yt_summary.schemas.enums import LLMProvidersEnum, SummarisationModesEnum
from yt_summary.schemas.models import LLMModel
from yt_summary.summarisers.refined_summariser import RefinedSummariser
from yt_summary.summarisers.simple_summariser import SimpleSummariser


async def get_youtube_summary(
    url: str,
    llm_provider: LLMProvidersEnum = LLMProvidersEnum.OPENAI,
    model_name: str = "gpt-5-mini-2025-08-07",
    mode: SummarisationModesEnum = SummarisationModesEnum.COMPACT,
    languages: list[str] | None = None,
    *,
    preserve_formatting: bool = False,
    proxy_config: ProxyConfig | None = None,
    http_client: Session | None = None,
) -> str:
    """Run the summarisation pipeline.

    Args:
        url: The YouTube video URL.
        llm_provider: The LLM provider to use. Defaults to "openai".
        model_name: The model name to use. Defaults to "gpt-5-mini-2025-08-07".
        mode: The summarisation mode. Defaults to "simple".
        languages: A list of language codes in a descending priority. For
            example, if this is set to ["de", "en"] it will first try to fetch the
            german transcript (de) and then fetch the english transcript (en) if
            it fails to do so. This defaults to ["en"].
        preserve_formatting: whether to keep select HTML text formatting
        proxy_config: Optional ProxyConfig for youtube-transcript-api
        http_client: Optional requests.Session for youtube-transcript-api

    Returns:
        str: The summary of the YouTube video.

    """
    transcript = await TranscriptExtractor(proxy_config=proxy_config, http_client=http_client).fetch(
        url, languages=languages if languages else ["en"], preserve_formatting=preserve_formatting
    )
    match mode:
        case SummarisationModesEnum.COMPACT:
            summariser = SimpleSummariser(llm=LLMModel(provider=LLMProvidersEnum(llm_provider), model=model_name))
        case SummarisationModesEnum.REFINED:
            summariser = RefinedSummariser(llm=LLMModel(provider=LLMProvidersEnum(llm_provider), model=model_name))
    return await summariser.summarise(transcript)


if __name__ == "__main__":
    import asyncio

    url = "https://www.youtube.com/watch?v=923G1s8QNAM"
    url = "https://youtu.be/ybWUK1dGRm8?si=BZzQxwIm2WmDVnpw"
    summary = asyncio.run(get_youtube_summary(url))
    print(summary)
