"""Run PyEqSolver: read equations, solve them, and write the JSON result."""

import sys

from pyeqsolver import EquationParser, GaussianSolver, JSONExporter
from pyeqsolver.exceptions import PyEqSolverError

INPUT_PATH = "data/input_equations.txt"
OUTPUT_PATH = "data/solution.json"


def main() -> int:
    """Solve the system in INPUT_PATH and return the exit status."""
    exporter = JSONExporter(output_path=OUTPUT_PATH)

    try:
        parser = EquationParser(file_path=INPUT_PATH)
        matrix, variables = parser.parse()

        solver = GaussianSolver(matrix=matrix, variables=variables)
        solutions = solver.solve()

        exporter.save(solutions=solutions, metadata=solver.get_metadata())
        print(f"Solved. Results written to {OUTPUT_PATH}")
        return 0

    except (PyEqSolverError, FileNotFoundError) as error:
        exporter.save_error(error)
        print(f"Could not solve the system: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())