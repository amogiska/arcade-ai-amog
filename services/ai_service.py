"""Service for AI-powered analysis using OpenAI."""

from pathlib import Path

import click
import openai

from flow_types.api_models import InteractionsResponse, SummaryResponse
from flow_types.chunk_models import ChunkInfo, FlowChunk, FlowMetadata
from flow_types.flow_types import FlowData


class AIService:
    """Service for handling AI-powered analysis operations."""

    PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

    # Default model configuration
    DEFAULT_CHUNK_PROCESSING_MODEL = "gpt-5-mini"
    DEFAULT_SUMMARY_MODEL = "gpt-5"

    def __init__(
        self,
        api_key: str,
        max_steps_per_chunk: int = 10,
        chunk_processing_model: str | None = None,
        summary_model: str | None = None,
    ):
        """
        Initialize the AI service with an OpenAI API key.

        Args:
            api_key: OpenAI API key
            max_steps_per_chunk: Maximum number of steps to process per chunk (default: 10)
            chunk_processing_model: Model for processing individual chunks (default: gpt-4o-mini)
            summary_model: Model for generating summaries (default: gpt-4o)
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.max_steps_per_chunk = max_steps_per_chunk

        # Use provided models or fall back to defaults
        self.chunk_processing_model = chunk_processing_model or self.DEFAULT_CHUNK_PROCESSING_MODEL
        self.summary_model = summary_model or self.DEFAULT_SUMMARY_MODEL

    def _load_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt from the prompts directory.

        Args:
            prompt_name: Name of the prompt file (without .txt extension)

        Returns:
            The prompt content as a string
        """
        prompt_path = self.PROMPTS_DIR / f"{prompt_name}.txt"
        return prompt_path.read_text()

    def _chunk_flow_data(self, flow_data: FlowData) -> list[FlowChunk]:
        """
        Split flow data into manageable chunks to avoid context size limits.

        Strategy:
        - Keep metadata (name, useCase, etc.) in each chunk
        - Split steps into configurable groups (max_steps_per_chunk)
        - Associate relevant capturedEvents with each chunk based on timing

        Args:
            flow_data: The complete flow data

        Returns:
            List of strongly-typed flow data chunks
        """
        steps = flow_data.get("steps", [])
        captured_events = flow_data.get("capturedEvents", [])

        # If the flow is small enough, return it as a single chunk
        if len(steps) <= self.max_steps_per_chunk:
            # Create a single chunk with all data
            chunk_info = ChunkInfo(chunk_index=0, total_chunks=1, steps_in_chunk=len(steps))
            return [
                FlowChunk(
                    name=flow_data.get("name", "Untitled Flow"),
                    useCase=flow_data.get("useCase", "unknown"),
                    description=flow_data.get("description", ""),
                    aspectRatio=flow_data.get("aspectRatio"),
                    steps=steps,
                    capturedEvents=captured_events,
                    chunk_info=chunk_info,
                )
            ]

        chunks: list[FlowChunk] = []
        total_chunks = (len(steps) + self.max_steps_per_chunk - 1) // self.max_steps_per_chunk

        # Create metadata that will be included in each chunk
        metadata = FlowMetadata(
            name=flow_data.get("name", "Untitled Flow"),
            use_case=flow_data.get("useCase", "unknown"),
            description=flow_data.get("description", ""),
            aspect_ratio=flow_data.get("aspectRatio"),
        )

        # Split steps into chunks
        for i in range(0, len(steps), self.max_steps_per_chunk):
            chunk_steps = steps[i : i + self.max_steps_per_chunk]
            chunk_index = i // self.max_steps_per_chunk

            # Create chunk info
            chunk_info = ChunkInfo(
                chunk_index=chunk_index,
                total_chunks=total_chunks,
                steps_in_chunk=len(chunk_steps),
            )

            # Create a strongly-typed chunk
            chunk = FlowChunk(
                name=metadata.name,
                useCase=metadata.use_case,
                description=metadata.description,
                aspectRatio=metadata.aspect_ratio,
                steps=chunk_steps,
                capturedEvents=captured_events,  # Include all events for context
                chunk_info=chunk_info,
            )
            chunks.append(chunk)

        return chunks

    def _process_chunk(self, chunk: FlowChunk, chunk_index: int, total_chunks: int) -> list[str]:
        """
        Process a single chunk of flow data to extract interactions.

        Args:
            chunk: A strongly-typed chunk of flow data
            chunk_index: Index of this chunk (0-based)
            total_chunks: Total number of chunks in the flow

        Returns:
            List of interactions found in this chunk
        """
        # Load the prompt template
        prompt_template = self._load_prompt("identify_interactions")

        # Convert chunk to JSON using Pydantic's serialization
        flow_chunk_json = chunk.model_dump_json(indent=2, by_alias=True)
        prompt = prompt_template.format(flow_chunk=flow_chunk_json)

        # Build JSON Schema from Pydantic model
        schema = InteractionsResponse.model_json_schema()

        try:
            response = self.client.chat.completions.create(
                model=self.chunk_processing_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing user interaction flows and extracting meaningful actions from technical data.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "interactions_response",
                        "schema": schema,
                        "strict": True,
                    },
                },
                temperature=0.3,
            )

            content = response.choices[0].message.content
            if content:
                interactions_response = InteractionsResponse.model_validate_json(content)
                return interactions_response.interactions

        except Exception as e:
            click.echo(f"   Warning: Error processing chunk {chunk_index + 1}/{total_chunks}: {e}")

        return []

    def identify_interactions(self, flow_data: FlowData) -> list[str]:
        """
        Identify and extract user interactions from the flow data.
        Uses chunking to handle large flows and avoid context size limits.

        Args:
            flow_data: The parsed flow.json data

        Returns:
            List of human-readable interaction descriptions
        """
        # Chunk the flow data
        chunks = self._chunk_flow_data(flow_data)
        total_chunks = len(chunks)

        if total_chunks > 1:
            click.echo(f"   Processing flow in {total_chunks} chunks...")

        # Process each chunk
        all_interactions: list[str] = []
        for i, chunk in enumerate(chunks):
            if total_chunks > 1:
                click.echo(f"   Analyzing chunk {i + 1}/{total_chunks}...", nl=False)

            interactions = self._process_chunk(chunk, i, total_chunks)
            all_interactions.extend(interactions)

            if total_chunks > 1:
                click.echo(f" found {len(interactions)} interactions")

        return all_interactions

    def generate_summary(self, flow_data: FlowData, interactions: list[str]) -> str:
        """
        Generate a human-friendly summary of what the user was trying to accomplish.

        Args:
            flow_data: The parsed flow.json data
            interactions: List of identified interactions

        Returns:
            Human-friendly summary text
        """
        # Load the prompt template
        prompt_template = self._load_prompt("generate_summary")

        # Create the prompt for summary generation
        interactions_text = "\n".join(f"- {interaction}" for interaction in interactions)
        prompt = prompt_template.format(
            flow_name=flow_data.get("name", "Untitled Flow"),
            use_case=flow_data.get("useCase", "unknown"),
            interactions_text=interactions_text,
        )

        # Build JSON Schema from Pydantic model with strict enforcement
        schema = SummaryResponse.model_json_schema()

        response = self.client.chat.completions.create(
            model=self.summary_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating engaging, human-friendly narratives from technical user interaction data.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "summary_response",
                    "schema": schema,
                    "strict": True,
                },
            },
            temperature=0.5,
        )

        # Parse the response using Pydantic for type safety
        content = response.choices[0].message.content
        if content:
            try:
                summary_response = SummaryResponse.model_validate_json(content)
                return summary_response.summary
            except Exception as e:
                click.echo(f"   Warning: Could not parse AI response: {e}")
                return "Unable to generate summary."

        return "Unable to generate summary."

    def create_social_image(self, flow_data: FlowData, summary: str, output_path: Path) -> None:
        """
        Create a creative social media image representing the flow.

        Args:
            flow_data: The parsed flow.json data
            summary: The generated summary text
            output_path: Where to save the generated image
        """
        # TODO: Implement social media image generation
        # Use DALL-E or similar to create an engaging image
        pass
