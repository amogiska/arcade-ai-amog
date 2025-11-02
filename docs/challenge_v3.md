# Challenge V3 Implementation

## What it does

Takes an Arcade `flow.json` file, analyzes it with OpenAI models, and generates:
- Complete list of ALL user interactions extracted from the flow
- Human-readable summary (generated from the most meaningful interactions)
- AI-generated social media image representing the flow
- Markdown report with all the above

## Implementation

Modular architecture with intelligent semantic ranking for scalability:

### Core Services

1. **FlowService**: Parse and load flow.json files
2. **AIService**: Handle all OpenAI API interactions
   - **Chunking**: Splits large flows into configurable chunks (default 10 steps/chunk)
   - **Interaction extraction**: Processes each chunk with gpt-5-mini
   - **Embeddings-based ranking**: Uses semantic embeddings + MMR algorithm to select meaningful interactions
   - **Summary generation**: Creates narrative with gpt-5 from filtered interactions
   - **Image generation**: Creates social media images with gpt-image-1
3. **ReportService**: Generate markdown reports with ALL interactions

### Key Features

**Smart Chunking**
- Automatically splits flows exceeding `max_steps_per_chunk`
- Maintains metadata (name, useCase, description) in each chunk
- Includes all capturedEvents for context
- Processes chunks sequentially with progress tracking

**Embeddings-Based Interaction Ranking**
- Uses `text-embedding-3-small` for semantic understanding
- Applies natural language query: *"User completed tasks. User submitted forms..."*
- Calculates semantic similarity between query and each interaction
- **MMR (Maximal Marginal Relevance)** algorithm ensures:
  - ✅ **Importance**: High similarity to query (70% weight)
  - ✅ **Diversity**: Low redundancy with selected interactions (30% weight)
- Handles unlimited interactions without context limits
- Ultra cost-efficient: ~$0.0002 per 500 interactions

**Image Generation**
- Uses gpt-image-1 model (only supported model)
- Returns base64 encoded PNG (1024x1024)
- Validates model at service initialization (fail-fast)
- Prompt template in `prompts/generate_image.txt`

**Configurable Models**
- `CHUNK_PROCESSING_MODEL` (default: gpt-5-mini)
- `SUMMARY_MODEL` (default: gpt-5)
- `IMAGE_MODEL` (default: gpt-image-1, only supported)
- `EMBEDDING_MODEL` (default: text-embedding-3-small)

### Architecture

```
Flow JSON
    ↓
[Chunking - Split large flows]
    ↓
[Extract Interactions - All chunks]
    ↓
ALL Interactions (e.g., 500)
    ↓
[Embeddings + MMR Ranking]
  - Embed query + interactions
  - Calculate semantic similarity
  - Apply MMR for diversity
    ↓
Top N Interactions (e.g., 50)
    ↓
[Generate Summary - From filtered set]
    ↓
[Generate Report - Shows ALL interactions]
```

### Type Safety

- Pydantic models for all API responses (`flow_types/`)
- Strongly-typed flow data structures
- JSON Schema validation with strict mode
- Full mypy type checking

## Improvements from V2

✅ **Embeddings-based ranking**: Semantic understanding instead of heuristics or LLM calls
✅ **MMR algorithm**: Balances importance and diversity, removes redundant interactions
✅ **No context limits**: Can handle thousands of interactions via embeddings
✅ **Complete reports**: Summary uses filtered interactions, report shows all interactions


## Configuration Example

```bash
# Optimize for cost (smaller models)
uv run main.py \
  --chunk-processing-model gpt-5-mini \
  --summary-model gpt-5-mini \
  --embedding-model text-embedding-3-small \
  --max-interactions-for-summary 30

# Optimize for quality (larger models)
uv run main.py \
  --chunk-processing-model gpt-5 \
  --summary-model gpt-5 \
  --embedding-model text-embedding-3-large \
  --max-interactions-for-summary 100
```

