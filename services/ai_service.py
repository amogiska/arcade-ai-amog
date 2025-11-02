"""Service for AI-powered analysis using OpenAI."""

from pathlib import Path

import click
import numpy as np
import openai

from flow_types.api_models import InteractionsResponse, SummaryResponse
from flow_types.chunk_models import ChunkInfo, FlowChunk, FlowMetadata
from flow_types.flow_types import FlowData
from services.image_utils import build_image_prompt, save_generated_image


class AIService:
    """Service for handling AI-powered analysis operations."""

    PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

    # Default model configuration
    DEFAULT_CHUNK_PROCESSING_MODEL = "gpt-5-mini"
    DEFAULT_SUMMARY_MODEL = "gpt-5"
    DEFAULT_IMAGE_MODEL = "gpt-image-1"
    DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

    def __init__(
        self,
        api_key: str,
        max_steps_per_chunk: int = 10,
        chunk_processing_model: str | None = None,
        summary_model: str | None = None,
        image_model: str | None = None,
        embedding_model: str | None = None,
        max_interactions_for_summary: int = 50,
    ):
        """
        Initialize the AI service with an OpenAI API key.

        Args:
            api_key: OpenAI API key
            max_steps_per_chunk: Maximum number of steps to process per chunk (default: 10)
            chunk_processing_model: Model for processing individual chunks (default: gpt-5-mini)
            summary_model: Model for generating summaries (default: gpt-5)
            image_model: Model for generating images (default: gpt-image-1, only gpt-image-1 is supported)
            embedding_model: Model for generating embeddings (default: text-embedding-3-small)
            max_interactions_for_summary: Maximum number of interactions to use for summary generation (default: 50)

        Raises:
            ValueError: If image_model is not 'gpt-image-1'
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.max_steps_per_chunk = max_steps_per_chunk
        self.max_interactions_for_summary = max_interactions_for_summary

        # Use provided models or fall back to defaults
        self.chunk_processing_model = chunk_processing_model or self.DEFAULT_CHUNK_PROCESSING_MODEL
        self.summary_model = summary_model or self.DEFAULT_SUMMARY_MODEL
        self.image_model = image_model or self.DEFAULT_IMAGE_MODEL
        self.embedding_model = embedding_model or self.DEFAULT_EMBEDDING_MODEL

        # Validate image model early
        if self.image_model != "gpt-image-1":
            raise ValueError(
                f"Only 'gpt-image-1' model is currently supported for image generation. "
                f"Got: '{self.image_model}'"
            )

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

    def _embedding_based_filter_interactions(
        self,
        interactions: list[str],
        target_count: int,
        flow_data: FlowData | None = None,
    ) -> list[str]:
        """
        Use AI embeddings to semantically rank and filter interactions.

        Creates a natural language query describing what we're looking for
        (important, meaningful actions), then finds interactions most similar
        to that query using semantic embeddings.

        Args:
            interactions: List of all interactions
            target_count: Number of interactions to keep
            flow_data: Optional flow data to incorporate context

        Returns:
            Top N interactions by semantic relevance to "importance"
        """
        # Build query using concrete action examples (works better than meta-descriptions)
        query_parts = [
            "User completed tasks. User submitted forms. User made decisions. "
            "User entered data. User confirmed actions. User achieved goals. "
            "User created something. User configured settings. User uploaded files. "
            "User saved changes. User published content. User finalized work."
        ]

        # Optionally add flow-specific context for better targeting
        if flow_data:
            flow_name = flow_data.get("name", "")
            use_case = flow_data.get("useCase", "")
            description = flow_data.get("description", "")

            if flow_name and flow_name != "Untitled Flow":
                query_parts.append(f"User actions in {flow_name}.")
            if use_case and use_case not in ["unknown", "other"]:
                query_parts.append(f"Actions related to {use_case}.")
            if description:
                # Take first sentence of description
                first_sentence = description.split(".")[0] + "."
                query_parts.append(f"User {first_sentence}")

        query_text = " ".join(query_parts)

        try:
            # Embed query + all interactions in one API call
            all_texts = [query_text] + interactions
            response = self.client.embeddings.create(model=self.embedding_model, input=all_texts)

            # Extract embeddings
            query_embedding = np.array(response.data[0].embedding)
            interaction_embeddings = np.array([d.embedding for d in response.data[1:]])

            # Calculate cosine similarity to query
            def cosine_similarity(a: "np.ndarray", b: "np.ndarray") -> float:
                return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

            similarities = np.array(
                [cosine_similarity(emb, query_embedding) for emb in interaction_embeddings]
            )

            # Apply Maximal Marginal Relevance for diversity
            selected_indices = self._mmr_select_indices(
                interaction_embeddings, similarities, target_count
            )

            return [interactions[i] for i in selected_indices]

        except Exception as e:
            click.echo(f"   Warning: Embeddings failed ({e}), using fallback")
            # Fallback: just return first N
            return interactions[:target_count]

    def _mmr_select_indices(
        self,
        embeddings: "np.ndarray",
        importance_scores: "np.ndarray",
        target_count: int,
        lambda_param: float = 0.7,
    ) -> list[int]:
        """
        Maximal Marginal Relevance: Select diverse + important interactions.

        Balances:
        - Importance: High similarity to query
        - Diversity: Low similarity to already selected

        Args:
            embeddings: Numpy array of interaction embeddings
            importance_scores: Similarity scores to query
            target_count: Number to select
            lambda_param: Balance (0.7 = 70% importance, 30% diversity)

        Returns:
            Indices of selected interactions
        """
        selected_indices: list[int] = []
        remaining_indices = list(range(len(embeddings)))

        # Select most important first
        first_idx = int(np.argmax(importance_scores))
        selected_indices.append(first_idx)
        remaining_indices.remove(first_idx)

        # Iteratively select interactions balancing importance + diversity
        while len(selected_indices) < target_count and remaining_indices:
            best_score = -1.0
            best_idx: int | None = None

            for idx in remaining_indices:
                # Importance component
                importance = importance_scores[idx]

                # Diversity component: distance from already selected
                max_similarity_to_selected = max(
                    np.dot(embeddings[idx], embeddings[sel_idx])
                    / (np.linalg.norm(embeddings[idx]) * np.linalg.norm(embeddings[sel_idx]))
                    for sel_idx in selected_indices
                )
                diversity = 1 - max_similarity_to_selected

                # MMR score
                mmr_score = lambda_param * importance + (1 - lambda_param) * diversity

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            if best_idx is not None:
                selected_indices.append(best_idx)
                remaining_indices.remove(best_idx)
            else:
                break

        return selected_indices

    def _rank_interactions(
        self, flow_data: FlowData, interactions: list[str], max_interactions: int
    ) -> list[str]:
        """
        Rank interactions by importance using AI embeddings + MMR.

        Uses semantic embeddings to understand importance and MMR to ensure diversity.
        No LLM calls needed - faster, cheaper, and scales infinitely.

        Args:
            flow_data: The parsed flow.json data
            interactions: List of all identified interactions
            max_interactions: Maximum number of interactions to return

        Returns:
            List of the most meaningful interactions, limited to max_interactions
        """
        if len(interactions) <= max_interactions:
            return interactions

        original_count = len(interactions)
        click.echo(
            f"   Ranking {original_count} interactions using AI embeddings + MMR "
            f"to find top {max_interactions}..."
        )

        # Use embeddings + MMR for all ranking (no LLM needed)
        ranked_interactions = self._embedding_based_filter_interactions(
            interactions, max_interactions, flow_data
        )

        click.echo(f"   Selected {len(ranked_interactions)} most meaningful interactions")
        return ranked_interactions

    def generate_summary(
        self, flow_data: FlowData, interactions: list[str]
    ) -> tuple[str, list[str]]:
        """
        Generate a human-friendly summary of what the user was trying to accomplish.

        If there are too many interactions, they will be ranked and filtered to the most
        meaningful ones before generating the summary.

        Args:
            flow_data: The parsed flow.json data
            interactions: List of identified interactions

        Returns:
            Tuple of (summary text, interactions used for summary - may be filtered)
        """
        # Rank interactions if we have too many for the summary context
        if len(interactions) > self.max_interactions_for_summary:
            interactions = self._rank_interactions(
                flow_data, interactions, self.max_interactions_for_summary
            )

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
                return summary_response.summary, interactions
            except Exception as e:
                click.echo(f"   Warning: Could not parse AI response: {e}")
                return "Unable to generate summary.", interactions

        return "Unable to generate summary.", interactions

    def create_social_image(self, flow_data: FlowData, summary: str, output_path: Path) -> None:
        """
        Create a creative social media image representing the flow.

        Note: Only gpt-image-1 model is supported (validated at initialization).

        Args:
            flow_data: The parsed flow.json data
            summary: The generated summary text
            output_path: Where to save the generated image
        """
        flow_name = flow_data.get("name", "Untitled Flow")
        use_case = flow_data.get("useCase", "unknown")

        # Load the prompt template and build the image generation prompt
        prompt_template = self._load_prompt("generate_image")
        image_prompt = build_image_prompt(prompt_template, flow_name, use_case, summary)

        try:
            click.echo("   Generating social media image...")

            # Generate the image using OpenAI's image generation API (gpt-image-1)
            # Note: gpt-image-1 returns base64 encoded images by default
            response = self.client.images.generate(
                model=self.image_model,
                prompt=image_prompt,
                n=1,
                size="1024x1024",
            )

            # Save the generated image
            save_generated_image(response.data, output_path)

        except Exception as e:
            click.echo(f"   Warning: Could not generate image: {e}")
