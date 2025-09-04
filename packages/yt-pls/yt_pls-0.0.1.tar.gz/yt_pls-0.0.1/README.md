<h1 align="center">yt-summary</h1>

<p align="center">
    <a href="https://www.python.org/downloads/release/python-3131/">
        <img src="https://img.shields.io/badge/python-3.13-blue.svg" alt="Python 3.13">
    </a>
    <a href="https://github.com/astral-sh/ty">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Linting: Ruff">
    </a>
    <a href="LICENSE">
        <img alt="License" src="https://img.shields.io/static/v1?logo=MIT&color=Blue&message=MIT&label=License"/>
    </a>
</p>

<p align="center">
A tool to generate YouTube video summaries with LlmaIndex
</p>

## Install

### pip

```bash
pip install yt-summary
```

If you want to use the Gemini and/or Claude models, you need to install the optional dependencies:
```bash
pip install yt-summary[google]
pip install yt-summary[anthropic]

# or
pip install yt-summary[all]
```

### Development
Install [uv](https://github.com/astral-sh/uv) and run:
```bash
git clone https://github.com/nelnn/yt-summary.git
cd yt-summary
make install
source .venv/bin/activate
```

## CLI
Export your API key(s) as an environment variable:
```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

Then execute
```bash
yt-summary [url/video_id]
```

You can specify the LLM provider and model:
```bash
yt-summary --provider openai --model gpt-5-mini-2025-08-07 [url/video_id]
```

You can also specify the summariser type:
```bash
yt-summary --summariser refined [url/video_id]
```

To save the output to a file, for example in markdown:
```bash
yt-summary [url/video_id] > summary.md
```

## API
You can also use yt-summary as a library:
```python
from yt_summary.run import get_youtube_summary

summary = await get_youtube_summary("https://www.youtube.com/watch?v=abc123")
```

Remember to export your LLM API key as an environment variable before running
the function. Alternatively, you can save them in a `.env` file in your project
root directory.


### Transcript Extractor
To fetch the transcript and metadata:
```python
from yt_summary.extractors import TranscriptExtractor

url = "url or video id"
transcript_extractor = TranscriptExtractor()
transcript_raw = await transcript_extractor.fetch(url)
```

This will return a Pydantic model `YoutubeTranscriptRaw` which looks like:
```python
YoutubeTranscriptRaw(
    metadata=YoutubeMetadata(
        video_id="abc123",
        title="Video Title",
        author="Author Name",
        channel_id="channel123",
        video_url="https://www.youtube.com/watch?v=abc123",
        channel_url="https://www.youtube.com/channel/channel123",
        thumbnail_url="https://i.ytimg.com/vi/abc123/hqdefault.jpg",
        is_generated=True,
        language="English (auto-generated)",
        language_code="en",
    ),
    text="[00:00 (0s)] First sentence. Second sentence. [00:10 (10s)] Third sentence...",
)
```
> **Note**: The extractor is just a wrapper around
> [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
> which you can pass the same parameters to `fetch` as you would to
> `YouTubeTranscriptApi.fetch` but here we stitch the transcript snippets into
> a single string with timestamps embedded in the text. You can also pass the
> proxy settings to `TranscriptExtractor` as you would to
> `YouTubeTranscriptApi`.

### Summariser
There are currently two summariser implementations: `CompactSummariser` and
`RefineSummariser`.

`CompactSummariser` lists metadata, high level summary and
Q&A with timestamps. It utilises the `DocumentSummaryIndex` from LLamaIndex.

`RefineSummariser` achieves the same by chunking the transcript to generate
summaries for each chunk before consolidating them by making multiple calls to
the LLM asynchronously. Be aware of the rate limits of your chosen LLM
provider.

For example, to generate summary with `CompactSummariser`:
```python
from yt_summary.extractors import TranscriptExtractor
from yt_summary.schemas import LLMModel, LLMProvidersEnum
from yt_summary.summarisers import CompactSummariser, RefinedSummariser

transcript_extractor = TranscriptExtractor()
transcript_raw = await transcript_extractor.fetch(url)
summariser = CompactSummariser(
    llm=LLMModel(
        provider=LLMProvidersEnum.OPENAI,
        model="gpt-5-mini-2025-08-07",
    )
)
summary = await summariser.summarise(transcript)
```

> The repository is under development, expect breaking changes.
> Sugguestions and contributions are welcome!
