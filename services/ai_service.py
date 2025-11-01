"""Service for AI-powered analysis using OpenAI."""

import json
from pathlib import Path

import click
import openai

from flow_types.api_models import InteractionsResponse, SummaryResponse
from flow_types.flow_types import FlowData


class AIService:
    """Service for handling AI-powered analysis operations."""

    def __init__(self, api_key: str):
        """
        Initialize the AI service with an OpenAI API key.

        Args:
            api_key: OpenAI API key
        """
        self.client = openai.OpenAI(api_key=api_key)

    def identify_interactions(self, flow_data: FlowData) -> list[str]:
        """
        Identify and extract user interactions from the flow data.

        Args:
            flow_data: The parsed flow.json data

        Returns:
            List of human-readable interaction descriptions
        """
        # Prepare the flow data as a JSON string
        flow_json = json.dumps(flow_data, indent=2)

        # Create the prompt for analyzing interactions
        prompt = f"""
Analyze the following Arcade flow.json data and identify all meaningful user interactions.
Focus on the 'capturedEvents' and 'steps' to understand what actions the user took.

Extract a list of clear, human-readable descriptions of each interaction.
Each interaction should be a concise sentence describing what the user did.

Flow data:
{flow_json}
"""

        # Build JSON Schema from Pydantic model with strict enforcement
        schema = InteractionsResponse.model_json_schema()

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
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
                    "strict": True,  # Hard enforcement by the API
                },
            },
            temperature=0.3,
        )

        # Parse the response using Pydantic for type safety
        content = response.choices[0].message.content
        if content:
            try:
                interactions_response = InteractionsResponse.model_validate_json(content)
                return interactions_response.interactions
            except Exception as e:
                click.echo(f"   Warning: Could not parse AI response: {e}")
                return []

        return []

    def generate_summary(self, flow_data: FlowData, interactions: list[str]) -> str:
        """
        Generate a human-friendly summary of what the user was trying to accomplish.

        Args:
            flow_data: The parsed flow.json data
            interactions: List of identified interactions

        Returns:
            Human-friendly summary text
        """
        # Create the prompt for summary generation
        interactions_text = "\n".join(f"- {interaction}" for interaction in interactions)
        prompt = f"""
Analyze this user's flow and create a human-friendly narrative summary.

Flow Name: {flow_data.get("name", "Untitled Flow")}
Use Case: {flow_data.get("useCase", "unknown")}

User Interactions:
{interactions_text}

Create a compelling narrative that explains:
1. What the user was trying to accomplish (the goal)
2. The key actions they took
3. A brief, engaging summary of the entire flow
"""

        # Build JSON Schema from Pydantic model with strict enforcement
        schema = SummaryResponse.model_json_schema()

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
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
