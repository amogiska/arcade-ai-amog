"""Service for loading and parsing flow data."""

import json
from pathlib import Path

from flow_types.flow_types import FlowData


class FlowService:
    """Service for handling flow data operations."""

    @staticmethod
    def load_flow_data(flow_file: Path) -> FlowData:
        """
        Load and parse the flow.json file.

        Args:
            flow_file: Path to the flow.json file

        Returns:
            Parsed flow data with type validation

        Raises:
            FileNotFoundError: If the flow file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        with open(flow_file) as f:
            data: FlowData = json.load(f)
            return data
