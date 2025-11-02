# Arcade AI Interview Challenge

CLI tool to analyze Arcade flow recordings and generate comprehensive report and social media image.

**Example output files from a sample run ([`report.md`](report.md) and [`flow_image.png`](flow_image.png)) are included in this repository.**

## Approach

This tool achieves three key goals while maintaining scalability:

1. **Identify User Interactions** - Extract meaningful actions from flow recordings
2. **Generate Human-Friendly Summaries** - Create narrative summaries of user journeys
3. **Create Social Media Images** - Generate visual representations for sharing

**Scalability Features:**
- **Intelligent Chunking** - Processes large flows in manageable chunks to avoid context limits
- **Embeddings-Based Ranking** - Uses semantic embeddings (text-embedding-3-small) + MMR algorithm to select the most meaningful interactions for summary generation, enabling the system to handle flows with hundreds or thousands of interactions

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```
   
   This will install both production dependencies (click, openai, numpy) and development dependencies (ruff, mypy).

2. **Set up your environment:**
   
   Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```
   
   See [Model Configuration](#model-configuration) below for customizing AI models.

## Usage

Basic usage (analyzes `flow.json` and generates `report.md` and `flow_image.png`):
```bash
uv run main.py
```

This will generate:
- **`report.md`** - Markdown report with summary and all user interactions
- **`flow_image.png`** - AI-generated social media image (1024x1024 PNG)

With custom options:
```bash
uv run main.py --flow-file path/to/flow.json --output my_report.md --image-output social.png
```

## CLI Options

- `--flow-file PATH`: Path to the flow.json file to analyze (default: `flow.json`)
- `-o, --output PATH`: Output markdown file path (default: `report.md`)
- `--image-output PATH`: Output path for the generated social media image (default: `flow_image.png`)
- `--api-key TEXT`: OpenAI API key (or set `OPENAI_API_KEY` environment variable)
- `--max-steps-per-chunk INT`: Maximum steps to process per chunk (default: `10`)
- `--max-interactions-for-summary INT`: Maximum interactions to use for summary generation (default: `50`)
- `--chunk-processing-model TEXT`: Model for chunk processing (default: `gpt-5-mini`)
- `--summary-model TEXT`: Model for summary generation (default: `gpt-5`)
- `--image-model TEXT`: Model for image generation (default: `gpt-image-1`, only gpt-image-1 is supported)
- `--embedding-model TEXT`: Model for embeddings (default: `text-embedding-3-small`)
- `--help`: Show help message

## Model Configuration

The tool uses different OpenAI models for different tasks:

| Model | Default | Purpose |
|-------|---------|---------|
| Chunk Processing | `gpt-5-mini` | Analyzing individual flow chunks and extracting interactions |
| Summary | `gpt-5` | Generating creative, human-friendly summaries |
| Image | `gpt-image-1` | Generating social media images (only supported option) |
| Embedding | `text-embedding-3-small` | Semantic ranking of interactions for summary generation |

Configure via environment variables (in `.env` file) or CLI options:

```bash
# Environment variables
CHUNK_PROCESSING_MODEL=gpt-5-mini
SUMMARY_MODEL=gpt-5
IMAGE_MODEL=gpt-image-1
EMBEDDING_MODEL=text-embedding-3-small

# CLI options
uv run main.py --chunk-processing-model gpt-5 --embedding-model text-embedding-3-large
```

For available model options, refer to the [OpenAI API documentation](https://platform.openai.com/docs/models).

## Development

### Linting and Formatting

The project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting, and [mypy](https://mypy-lang.org/) for type checking.

**Format code:**
```bash
./scripts/format.sh
```

This will:
- Format code with ruff (auto-fixes style issues)
- Auto-fix linter issues where possible

**Check code quality:**
```bash
./scripts/lint.sh
```

This will:
- Run ruff linter to check for code quality issues
- Run mypy to check for type errors

Configuration is in `pyproject.toml`.
