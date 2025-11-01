"""Command-line interface commands."""

from pathlib import Path

import click
from dotenv import load_dotenv

from services import AIService, FlowService, ReportService

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
@click.option(
    "--max-steps-per-chunk",
    type=int,
    default=10,
    help="Maximum number of steps to process per chunk",
)
@click.option(
    "--chunk-processing-model",
    envvar="CHUNK_PROCESSING_MODEL",
    default="gpt-4o-mini",
    help="OpenAI model for chunk processing (or set CHUNK_PROCESSING_MODEL env variable)",
)
@click.option(
    "--summary-model",
    envvar="SUMMARY_MODEL",
    default="gpt-4o",
    help="OpenAI model for summary generation (or set SUMMARY_MODEL env variable)",
)
def analyze(
    flow_file: Path,
    output: Path,
    image_output: Path,
    api_key: str | None,
    max_steps_per_chunk: int,
    chunk_processing_model: str,
    summary_model: str,
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

    # Initialize services
    flow_service = FlowService()
    ai_service = AIService(
        api_key,
        max_steps_per_chunk=max_steps_per_chunk,
        chunk_processing_model=chunk_processing_model,
        summary_model=summary_model,
    )
    report_service = ReportService()

    # Display configuration
    click.echo(f"🤖 Models: chunk={chunk_processing_model}, summary={summary_model}")

    # Load flow data
    click.echo("📖 Loading flow data...")
    flow_data = flow_service.load_flow_data(flow_file)

    # Step 1: Identify user interactions
    click.echo("\n🔍 Step 1: Identifying user interactions...")
    interactions = ai_service.identify_interactions(flow_data)
    click.echo(f"   Found {len(interactions)} interactions")

    # Step 2: Generate summary
    click.echo("\n📝 Step 2: Generating human-friendly summary...")
    summary = ai_service.generate_summary(flow_data, interactions)

    # Step 3: Create social media image
    click.echo("\n🎨 Step 3: Creating social media image...")
    ai_service.create_social_image(flow_data, summary, image_output)
    click.echo(f"   Image saved to: {image_output}")

    # Step 4: Generate markdown report
    click.echo("\n📄 Step 4: Generating markdown report...")
    report_service.generate_report(interactions, summary, image_output, output)
    click.echo(f"   Report saved to: {output}")

    click.echo("\n✨ Analysis complete!")
