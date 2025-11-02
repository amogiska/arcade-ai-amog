"""Service for generating markdown reports."""

from pathlib import Path


class ReportService:
    """Service for handling report generation operations."""

    @staticmethod
    def generate_report(
        interactions: list[str],
        summary: str,
        image_path: Path,
        output_path: Path,
    ) -> None:
        """
        Generate the final markdown report.

        Args:
            interactions: List of all identified interactions
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
