"""High level summary."""

from llama_index.core import Document, DocumentSummaryIndex, PromptTemplate, get_response_synthesizer
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.response_synthesizers.type import ResponseMode

from yt_summary.schemas.models import YoutubeTranscriptRaw
from yt_summary.summarisers.base_summariser import BaseSummariser
from yt_summary.summarisers.templates import COMPACT_SUMMARY_QA_PROMPT_TEMPLATE


class SimpleSummariser(BaseSummariser):
    """Class for generating high level summaries from video transcripts."""

    async def summarise(self, transcript: YoutubeTranscriptRaw) -> str:
        """Generate a high level summary from the provided text.

        Args:
            transcript: The transcript to summarise.

        Returns:
            A high level summary of the transcript.

        """
        docs = Document(
            text=transcript.text, metadata=transcript.metadata.model_dump(), doc_id=transcript.metadata.video_id
        )
        splitter = SentenceSplitter(chunk_size=2048, chunk_overlap=200)
        response_synthesizer = get_response_synthesizer(
            llm=self.model.llm,
            text_qa_template=PromptTemplate(COMPACT_SUMMARY_QA_PROMPT_TEMPLATE),
            response_mode=ResponseMode.COMPACT,
            use_async=True,
        )
        index = DocumentSummaryIndex.from_documents(
            [docs],
            llm=self.model.llm,
            transformations=[splitter],
            response_synthesizer=response_synthesizer,
            embed_model=self.model.embed_model,
        )
        return index.get_document_summary(transcript.metadata.video_id)
