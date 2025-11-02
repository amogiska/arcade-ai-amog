"""Utilities for image generation and processing."""

import base64
from pathlib import Path
from typing import Any

import click


def build_image_prompt(template: str, flow_name: str, summary: str) -> str:
    """
    Build a descriptive prompt for social media image generation.

    Args:
        template: The prompt template string
        flow_name: Name of the flow
        summary: Generated summary text

    Returns:
        Formatted prompt for image generation
    """
    return template.format(flow_name=flow_name, summary=summary)


def save_generated_image(
    image_data: list[Any] | None, output_path: Path, source: str = "API"
) -> bool:
    """
    Save a generated image from OpenAI API response (gpt-image-1 base64 format only).

    Args:
        image_data: List of image data from OpenAI API response (can be None)
        output_path: Path where the image should be saved
        source: Source description for error messages

    Returns:
        True if successful, False otherwise
    """
    if not image_data or len(image_data) == 0:
        click.echo(f"   Warning: No image data returned from {source}")
        return False

    image_obj = image_data[0]

    # gpt-image-1 returns base64 encoded images
    if not hasattr(image_obj, "b64_json") or not image_obj.b64_json:
        click.echo(f"   Warning: No base64 image data returned from {source}")
        return False

    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_obj.b64_json)

        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the image
        output_path.write_bytes(image_bytes)
        click.echo(f"   ✓ Image saved to {output_path}")
        return True
    except Exception as e:
        click.echo(f"   Warning: Failed to decode/save base64 image: {e}")
        return False
