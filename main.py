import json
from pathlib import Path

import click
import openai
from dotenv import load_dotenv

from flow_types.api_models import InteractionsResponse, SummaryResponse
from flow_types.flow_types import FlowData

# Load environment variables from .env file
load_dotenv()


@click.command()
@click.option(
    "--flow-file",
    type=click.Path(exists=True, path_type=Path),
    default="flow.json",
    help="Path to the flow.json file to analyze",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="report.md",
    help="Output markdown file path",
)
@click.option(
    "--image-output",
    type=click.Path(path_type=Path),
    default="flow_image.png",
    help="Output path for the generated social media image",
)
@click.option(
    "--api-key",
    envvar="OPENAI_API_KEY",
    help="OpenAI API key (or set OPENAI_API_KEY env variable)",
)
def analyze(
    flow_file: Path, output: Path, image_output: Path, api_key: str | None
) -> None:
    """
    Analyze an Arcade flow.json file and generate a comprehensive report.

    This command will:
    1. Identify user interactions from the flow
    2. Generate a human-friendly summary
    3. Create a social media image
    4. Output everything to a markdown report
    """
    click.echo(f"Analyzing Arcade flow from: {flow_file}")

    # Validate API key
    if not api_key:
        raise click.UsageError(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
            "or use --api-key option."
        )

    # Load flow data
    click.echo("📖 Loading flow data...")
    flow_data = load_flow_data(flow_file)

    # Step 1: Identify user interactions
    click.echo("\n🔍 Step 1: Identifying user interactions...")
    interactions = identify_interactions(flow_data, api_key)
    click.echo(f"   Found {len(interactions)} interactions")

    # Step 2: Generate summary
    click.echo("\n📝 Step 2: Generating human-friendly summary...")
    summary = generate_summary(flow_data, interactions, api_key)

    # Step 3: Create social media image
    click.echo("\n🎨 Step 3: Creating social media image...")
    create_social_image(flow_data, summary, image_output, api_key)
    click.echo(f"   Image saved to: {image_output}")

    # Step 4: Generate markdown report
    click.echo("\n📄 Step 4: Generating markdown report...")
    generate_report(interactions, summary, image_output, output)
    click.echo(f"   Report saved to: {output}")

    click.echo("\n✨ Analysis complete!")


def load_flow_data(flow_file: Path) -> FlowData:
    """
    Load and parse the flow.json file.

    Args:
        flow_file: Path to the flow.json file

    Returns:
        Parsed flow data with type validation
    """
    with open(flow_file) as f:
        data: FlowData = json.load(f)
        return data


def identify_interactions(flow_data: FlowData, api_key: str) -> list[str]:
    """
    Identify and extract user interactions from the flow data.

    Args:
        flow_data: The parsed flow.json data
        api_key: OpenAI API key

    Returns:
        List of human-readable interaction descriptions
    """
    client = openai.OpenAI(api_key=api_key)

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

    response = client.chat.completions.create(
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


def generate_summary(flow_data: FlowData, interactions: list[str], api_key: str) -> str:
    """
    Generate a human-friendly summary of what the user was trying to accomplish.

    Args:
        flow_data: The parsed flow.json data
        interactions: List of identified interactions
        api_key: OpenAI API key

    Returns:
        Human-friendly summary text
    """
    client = openai.OpenAI(api_key=api_key)

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

    response = client.chat.completions.create(
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


def create_social_image(
    flow_data: FlowData, summary: str, output_path: Path, api_key: str
) -> None:
    """
    Create a creative social media image representing the flow.

    Args:
        flow_data: The parsed flow.json data
        summary: The generated summary text
        output_path: Where to save the generated image
        api_key: OpenAI API key
    """
    # TODO: Implement social media image generation
    # Use DALL-E or similar to create an engaging image
    pass


def generate_report(
    interactions: list[str], summary: str, image_path: Path, output_path: Path
) -> None:
    """
    Generate the final markdown report.

    Args:
        interactions: List of identified interactions
        summary: The generated summary
        image_path: Path to the generated social media image
        output_path: Where to save the markdown report
    """
    # Build the markdown content
    markdown_lines = [
        "# Arcade Flow Analysis Report",
        "",
        "## Summary",
        "",
        summary,
        "",
        "## User Interactions",
        "",
    ]

    # Add interactions as a numbered list
    for i, interaction in enumerate(interactions, 1):
        markdown_lines.append(f"{i}. {interaction}")

    markdown_lines.extend(
        [
            "",
            "## Social Media Image",
            "",
            f"![Flow Visualization]({image_path})",
            "",
        ]
    )

    # Write to file
    output_path.write_text("\n".join(markdown_lines))


if __name__ == "__main__":
    analyze()
