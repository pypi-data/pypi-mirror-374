"""Pydantic models."""

from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.embeddings.openai.base import BaseEmbedding
from pydantic import BaseModel, HttpUrl

from yt_summary.schemas.enums import LLMProvidersEnum


class YoutubeMetadata(BaseModel):
    """YouTube video metadata model.

    Attributes:
        video_id: The unique identifier for the YouTube video.
        title: The title of the YouTube video.
        author: The author of the YouTube video.
        channel_id: The unique identifier for the YouTube channel.
        video_url: The URL of the YouTube video.
        channel_url: The URL of the YouTube channel.
        thumbnail_url: The URL of the YouTube video's thumbnail image.

    """

    video_id: str
    title: str
    author: str
    channel_id: str
    video_url: HttpUrl
    channel_url: HttpUrl
    thumbnail_url: HttpUrl | None = None
    is_generated: bool | None = None
    language: str | None = None
    language_code: str | None = None


class YoutubeTranscriptRaw(BaseModel):
    """YouTube video metadata with raw transcript.

    Attributes:
        metadata: The metadata of the YouTube video.
        text: transcript text.

    """

    metadata: YoutubeMetadata
    text: str


class LLMModel(BaseModel):
    """Language model configuration.

    Attributes:
        provider: The provider of the language model.
        model: The specific model to use.

    """

    provider: LLMProvidersEnum
    model: str


class LLMAndEmbeddingModel(BaseModel):
    """Language model and embedding model pair.

    Attributes:
        llm: The language model instance.
        embed_model: The embedding model instance.

    """

    llm: FunctionCallingLLM
    embed_model: BaseEmbedding
