"""Write the solution or an error to a JSON file."""

import json
import os


class JSONExporter:
    """Save solver results as JSON."""

    def __init__(self, output_path: str) -> None:
        """Store the path of the output file."""
        self.output_path = output_path

    def save(self, solutions: dict[str, float], metadata: dict) -> None:
        """Write a SUCCESS file with the rounded solution."""
        cleaned = {}
        for name, value in solutions.items():
            cleaned[name] = self._clean(value)

        data = {
            "status": "SUCCESS",
            "system_info": metadata,
            "solution": cleaned,
        }
        self._write(data)

    def save_error(self, exc: Exception) -> None:
        """Write an ERROR file with the exception name and message."""
        data = {
            "status": "ERROR",
            "error_type": type(exc).__name__,
            "message": str(exc),
        }
        self._write(data)

    def _clean(self, value: float) -> float:
        """Round to 4 decimals and turn -0.0 into 0.0."""
        value = round(value, 4)
        if value == 0:
            return 0.0
        return value

    def _write(self, data: dict) -> None:
        """Create the folder if needed, then write the JSON file."""
        folder = os.path.dirname(self.output_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)