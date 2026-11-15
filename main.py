"""Run PyEqSolver: read equations, solve them, and write the JSON result."""

import argparse
import sys

from pyeqsolver import EquationParser, GaussianSolver, JSONExporter
from pyeqsolver.exceptions import PyEqSolverError


def read_arguments() -> argparse.Namespace:
    """Read --input, --output and --precision from the command line."""
    parser = argparse.ArgumentParser(
        description="Solve a system of linear equations with Gaussian Elimination."
    )
    parser.add_argument(
        "--input",
        default="data/input_equations.txt",
        help="file with one equation per line (default: data/input_equations.txt)",
    )
    parser.add_argument(
        "--output",
        default="data/solution.json",
        help="JSON file to write the result to (default: data/solution.json)",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=4,
        help="number of decimal places in the answer (default: 4)",
    )
    return parser.parse_args()


def main() -> int:
    """Solve the system in the input file and return the exit status."""
    args = read_arguments()
    exporter = JSONExporter(output_path=args.output, precision=args.precision)

    try:
        parser = EquationParser(file_path=args.input)
        matrix, variables = parser.parse()

        solver = GaussianSolver(matrix=matrix, variables=variables)
        solutions = solver.solve()

        exporter.save(solutions=solutions, metadata=solver.get_metadata())
        print(f"Solved. Results written to {args.output}")
        return 0

    except (PyEqSolverError, FileNotFoundError) as error:
        exporter.save_error(error)
        print(f"Could not solve the system: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())