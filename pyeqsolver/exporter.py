"""Write the solution or an error to a JSON file."""

import json
import os


class JSONExporter:
    """Save solver results as JSON."""

    def __init__(self, output_path: str, precision: int = 4) -> None:
        """Store the output path and how many decimals to keep."""
        self.output_path = output_path
        self.precision = precision

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
        """Round to self.precision decimals and turn -0.0 into 0.0."""
        value = round(value, self.precision)
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