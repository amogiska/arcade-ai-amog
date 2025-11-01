# Challenge V1 Implementation

## What it does

Takes an Arcade `flow.json` file, sends it to GPT-4o-mini, and generates a markdown report with:
- List of user interactions extracted from the flow
- Human-readable summary of what the user was trying to accomplish
- Reference to a social media image (not yet generated)

## Implementation

Single CLI script (`main.py`) with four steps:

1. **load_flow_data**: Parse JSON file
2. **identify_interactions**: Send flow to GPT-4o-mini with JSON Schema to extract interaction list
3. **generate_summary**: Send flow + interactions to GPT-4o-mini to create narrative summary
4. **generate_report**: Write markdown file with interactions and summary

Uses Pydantic for response validation and Click for the CLI.

## Limitations

### Context size
Sends the entire flow.json as one prompt. Large flows (many steps/events) will:
- Hit GPT-4o-mini's 128K token limit
- Cost more
- Possibly fail

### No image generation
`create_social_image()` is a stub. The markdown report references an image that doesn't exist.

### Basic error handling
No retries, no graceful degradation, no resume capability for failed runs.

## V2 Plans

- Chunk large flows into smaller pieces to avoid context limits
- Actually generate the social media image with DALL-E
- Add retry logic and better error handling

