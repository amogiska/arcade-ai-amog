# Challenge V2 Implementation

## What it does

Takes an Arcade `flow.json` file, analyzes it with OpenAI models, and generates:
- List of user interactions extracted from the flow
- Human-readable summary of what the user was trying to accomplish
- AI-generated social media image representing the flow
- Markdown report with all the above

## Implementation

Modular architecture with service layer (`services/`) and CLI (`cli/commands.py`):

### Core Services

1. **FlowService**: Parse and load flow.json files
2. **AIService**: Handle all OpenAI API interactions
   - **Chunking**: Splits large flows into configurable chunks (default 10 steps/chunk)
   - **Interaction extraction**: Processes each chunk with gpt-4o-mini
   - **Summary generation**: Creates narrative with gpt-4o
   - **Image generation**: Creates social media images with gpt-image-1
3. **ReportService**: Generate markdown reports

### Key Features

**Smart Chunking**
- Automatically splits flows exceeding `max_steps_per_chunk`
- Maintains metadata (name, useCase, description) in each chunk
- Includes all capturedEvents for context
- Processes chunks in parallel

**Image Generation**
- Uses gpt-image-1 model (only supported model)
- Returns base64 encoded PNG (1024x1024)
- Validates model at service initialization (fail-fast)
- Prompt template in `prompts/generate_image.txt`

**Configuration**
- Configurable models via CLI options or environment variables
- `CHUNK_PROCESSING_MODEL` (default: gpt-4o-mini)
- `SUMMARY_MODEL` (default: gpt-4o)
- `IMAGE_MODEL` (default: gpt-image-1, only supported)

### Type Safety

- Pydantic models for all API responses (`flow_types/`)
- Strongly-typed flow data structures
- JSON Schema validation with strict mode

## Improvements from V1

✅ **Chunking**: Handles large flows by splitting into manageable pieces
✅ **Image generation**: Actually generates images (not a stub)
✅ **Service architecture**: Clean separation of concerns
✅ **Configuration**: Flexible model selection
✅ **Type safety**: Strong typing throughout


