# Arcade AI Interview Challenge

CLI tool to analyze Arcade flow recordings and generate comprehensive reports.

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```
   
   This will install both production dependencies (click, openai) and development dependencies (ruff, mypy).

2. **Set up your API key:**
   
   Create a `.env` file (don't commit this!):
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```
   
   Then load it:
   ```bash
   export $(cat .env | xargs)
   ```
   
   Or set it directly in your shell:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
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
- `--help`: Show help message

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

## Implementation Notes

The CLI is structured with the following functions to implement:

1. **`load_flow_data()`**: Loads and parses the flow.json file
2. **`identify_interactions()`**: Analyzes flow data to identify user actions
3. **`generate_summary()`**: Creates a human-friendly summary using AI
4. **`create_social_image()`**: Generates a social media image using DALL-E
5. **`generate_report()`**: Compiles everything into a markdown report

## Security

⚠️ **Never commit your API key!** The `.gitignore` file is configured to exclude:
- `.env` files
- Generated output files

