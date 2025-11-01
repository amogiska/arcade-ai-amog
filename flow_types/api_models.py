"""Pydantic models for OpenAI API structured responses."""

from pydantic import BaseModel, ConfigDict, Field


class InteractionsResponse(BaseModel):
    """Response model for user interactions extraction."""

    model_config = ConfigDict(extra="forbid")

    interactions: list[str] = Field(
        description="List of human-readable descriptions of user interactions"
    )


class SummaryResponse(BaseModel):
    """Response model for flow summary generation."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(
        description="A human-friendly narrative summary of what the user accomplished in the flow"
    )
    key_actions: list[str] = Field(description="List of key actions taken by the user")
    goal: str = Field(description="The primary goal or objective the user was trying to accomplish")
