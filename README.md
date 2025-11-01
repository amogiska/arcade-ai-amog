# Arcade AI Interview Challenge

CLI tool to analyze Arcade flow recordings and generate comprehensive reports.

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```
   
   This will install both production dependencies (click, openai) and development dependencies (ruff, mypy).

2. **Set up your environment:**
   
   Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```
   
   The `.env` file is automatically loaded by the CLI tool. You can also customize the AI models used:
   ```bash
   CHUNK_PROCESSING_MODEL=gpt-4o-mini  # Model for processing individual chunks
   SUMMARY_MODEL=gpt-4o                # Model for generating summaries
   ```

## Usage

Basic usage (uses default `flow.json` and outputs to `report.md`):
```bash
uv run main.py
```

With custom options:
```bash
uv run main.py --flow-file path/to/flow.json --output my_report.md --image-output social.png
```

## CLI Options

- `--flow-file PATH`: Path to the flow.json file to analyze (default: `flow.json`)
- `-o, --output PATH`: Output markdown file path (default: `report.md`)
- `--image-output PATH`: Output path for the generated social media image (default: `flow_image.png`)
- `--api-key TEXT`: OpenAI API key (or set `OPENAI_API_KEY` environment variable)
- `--max-steps-per-chunk INT`: Maximum steps to process per chunk (default: 10)
- `--chunk-processing-model TEXT`: Model for chunk processing (default: `gpt-4o-mini`, or set `CHUNK_PROCESSING_MODEL` env var)
- `--summary-model TEXT`: Model for summary generation (default: `gpt-4o`, or set `SUMMARY_MODEL` env var)
- `--help`: Show help message

### Model Configuration

The tool uses different OpenAI models for different tasks:

- **Chunk Processing Model** (`gpt-4o-mini` by default): Used for analyzing individual flow chunks. Optimized for speed and cost.
- **Summary Model** (`gpt-4o` by default): Used for generating creative summaries. Optimized for quality and narrative generation.

You can configure these via environment variables or CLI options:

```bash
# Via environment variables
export CHUNK_PROCESSING_MODEL=gpt-4o-mini
export SUMMARY_MODEL=gpt-4o

# Via CLI options
uv run main.py --chunk-processing-model gpt-4o --summary-model gpt-4o-mini
```

**Available Models:**
- `gpt-4o` - Latest GPT-4 Optimized (best quality, slower, more expensive)
- `gpt-4o-mini` - Smaller GPT-4 Optimized (good quality, faster, cost-effective)
- `gpt-4-turbo` - GPT-4 Turbo (high quality, balanced)
- `gpt-3.5-turbo` - GPT-3.5 Turbo (fastest, cheapest, lower quality)

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

## Architecture

The project follows a modular, service-oriented architecture:

```
├── main.py                 # Entry point
├── cli/                    # Command-line interface
│   └── commands.py         # CLI commands and orchestration
├── services/               # Business logic
│   ├── flow_service.py     # Flow data loading
│   ├── ai_service.py       # AI-powered analysis
│   └── report_service.py   # Report generation
└── flow_types/             # Type definitions
    ├── api_models.py       # Pydantic models
    └── flow_types.py       # Flow data types
```

### Key Services

1. **`FlowService`**: Loads and parses flow.json files
2. **`AIService`**: AI-powered analysis (interactions, summaries, images)
3. **`ReportService`**: Generates markdown reports

## Security

⚠️ **Never commit your API key!** The `.gitignore` file is configured to exclude:
- `.env` files
- Generated output files

