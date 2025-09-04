"""Command line interface for the YouTube summary tool."""

import argparse
import os
import sys
from importlib.metadata import PackageNotFoundError, version


class YTSummaryCLI:
    """Command line interface for the YouTube summary tool."""

    def __init__(self, args: list[str]) -> None:
        self._args = args

    async def run(self) -> str:
        """Run the CLI tool."""
        parsed_args = self._parse_args()

        if parsed_args.list_providers:
            from yt_summary.schemas.enums import LLMProvidersEnum

            return f"Supported LLM Providers: {[e.value for e in LLMProvidersEnum]}"

        if not parsed_args.url:
            return "Please provide a YouTube video URL or ID."

        try:
            if parsed_args.mode:
                from yt_summary.cli.errors import check_mode_type

                check_mode_type(parsed_args.mode)

            if parsed_args.provider:
                from yt_summary.cli.errors import check_provider_type

                check_provider_type(parsed_args.provider)

            from yt_summary.llm_config import llm_configs

            llm_config = llm_configs[parsed_args.provider]

            if not os.getenv(llm_config.key_name):
                return f"{llm_config.key_name} environment variable not set."

            from yt_summary.extractors.transcript import TranscriptExtractor
            from yt_summary.run.getters import summarisers
            from yt_summary.schemas.models import LLMModel

            llm_model = LLMModel(
                provider=parsed_args.provider,
                model=parsed_args.model or llm_config.default_model,
            )
            transcript_extractor = TranscriptExtractor()
            transcript = await transcript_extractor.fetch(parsed_args.url)
            summariser = summarisers[parsed_args.mode](llm=llm_model)
            return f"\n {await summariser.summarise(transcript)}"

        except Exception as e:
            return str(e)

    def _get_version(self) -> str:
        try:
            return version("yt-summary")
        except PackageNotFoundError:
            return "unknown"

    def _parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(prog="yt-summary", description="Youtube Summariser")
        parser.add_argument(
            "url",
            nargs="?",
            type=str,
            help=("video ID or URL of the Youtube video to summarize"),
        )

        parser.add_argument(
            "--version",
            "-v",
            action="version",
            version=f"%(prog)s {self._get_version()}",
            help="show the version number and exit",
        )

        parser.add_argument(
            "--list-providers",
            action="store_true",
            help="list all supported language model providers and exit",
        )

        parser.add_argument(
            "--provider",
            "-p",
            type=str,
            default="openai",
            help="language model provider to use. (default: openai)",
        )

        parser.add_argument(
            "--model",
            type=str,
            default=None,
            help="model name for the provider",
        )

        parser.add_argument(
            "--mode",
            "-m",
            type=str,
            default="compact",
            help=(
                "summarization mode: `compact` or `refined` (default: compact). "
                "`compact`: List metadata, high level summary and Q&A with timestamps. "
                "It utilises the `DocumentSummaryIndex` from LLamaIndex. "
                "`refined`: List metadata, high level summary and a detailed, timestamped summary of key points. "
                "It chunks the transcript (chunk_size=4096) and generates summaries for each chunk before"
                "consolidating them by making multiple calls to the LLM asynchronously. "
                "Be aware of the rate limits of your chosen LLM provider."
            ),
        )

        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

        return parser.parse_args(self._args)
