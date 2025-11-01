"""Pydantic models for AI service chunking."""

from pydantic import BaseModel, Field

from flow_types.flow_types import CapturedEvent, Step


class ChunkInfo(BaseModel):
    """Metadata about a chunk's position in the sequence."""

    chunk_index: int = Field(description="Zero-based index of this chunk")
    total_chunks: int = Field(description="Total number of chunks in the flow")
    steps_in_chunk: int = Field(description="Number of steps in this chunk")


class FlowMetadata(BaseModel):
    """Essential metadata from a flow, included in each chunk."""

    name: str = Field(description="Name of the flow")
    use_case: str = Field(description="Use case category for the flow")
    description: str = Field(default="", description="Optional description of the flow")
    aspect_ratio: float | None = Field(default=None, description="Aspect ratio of the flow")


class FlowChunk(BaseModel):
    """A chunk of flow data for processing.

    Contains metadata, a subset of steps, and all captured events for context.
    """

    name: str = Field(description="Name of the flow")
    use_case: str = Field(alias="useCase", description="Use case category")
    description: str = Field(default="", description="Flow description")
    aspect_ratio: float | None = Field(
        default=None, alias="aspectRatio", description="Aspect ratio"
    )
    steps: list[Step] = Field(description="Steps in this chunk")
    captured_events: list[CapturedEvent] = Field(
        alias="capturedEvents", description="All captured events for context"
    )
    chunk_info: ChunkInfo = Field(alias="chunk_info", description="Chunk position metadata")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True  # Allow both snake_case and camelCase
