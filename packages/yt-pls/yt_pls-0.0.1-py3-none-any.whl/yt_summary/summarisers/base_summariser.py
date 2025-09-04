"""Base class for text summarisation models."""

import abc
import os

from yt_summary.llm_config import llm_configs
from yt_summary.schemas.enums import LLMProvidersEnum
from yt_summary.schemas.models import LLMAndEmbeddingModel, LLMModel, YoutubeTranscriptRaw


class BaseSummariser(abc.ABC):
    """Base class for text summarisation models.

    Attributes:
        model: LLM model to use for summarisation.

    """

    def __init__(self, llm: LLMModel) -> None:
        self.model = self._get_model(llm)

    @staticmethod
    def _get_model(llm: LLMModel) -> LLMAndEmbeddingModel:
        """Get the LLM model based on the provided configuration.

        Args:
            llm: LLM model model.

        Returns:
            An instance of the selected LLM model.

        """
        opts = llm_configs[llm.provider]
        os.environ[opts.key_name] = os.getenv(opts.key_name) or opts.default_key
        embed_model = None
        match llm.provider:
            case LLMProvidersEnum.OPENAI:
                from llama_index.embeddings.openai import OpenAIEmbedding
                from llama_index.llms.openai import OpenAI

                llm_model = OpenAI(temperature=0, model=llm.model)
                embed_model = OpenAIEmbedding()
            case LLMProvidersEnum.GOOGLE:
                from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
                from llama_index.llms.google_genai import GoogleGenAI

                llm_model = GoogleGenAI(temperature=0, model=llm.model)
                embed_model = GoogleGenAIEmbedding()
            case LLMProvidersEnum.ANTHROPIC:
                from llama_index.embeddings.openai import OpenAIEmbedding
                from llama_index.llms.anthropic import Anthropic

                llm_model = Anthropic(temperature=0, model=llm.model)
                embed_model = OpenAIEmbedding()
        return LLMAndEmbeddingModel(llm=llm_model, embed_model=embed_model)

    @abc.abstractmethod
    async def summarise(self, transcript: YoutubeTranscriptRaw) -> str:
        """Abstract method to summarise text.

        Args:
            transcript: The transcript text to summarise.

        Returns:
            Summarised text.

        """
