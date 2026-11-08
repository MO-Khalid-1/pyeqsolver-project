# PyEqSolver

Solves a system of linear equations with Gaussian Elimination, written in
pure Python (standard library only). It reads equations from a text file
and writes the solution, or the error, to a JSON file.

## Requirements

- Python 3.10 or newer
- No third-party packages

## How to run

From the project folder:

    python main.py

On Windows you can also use `py main.py`.

It reads `data/input_equations.txt` and writes `data/solution.json`.
The program exits with status `0` on success and `1` on any error.

## How to run the tests

    py -m unittest discover -s tests -v

- `tests/test_parser.py` tests the parser.
- `tests/test_solver.py` tests the solver.
- `tests/test_exporter.py` tests the JSON exporter.
- Test input files are in `tests/data/`.

## Input file format

One equation per line:

    # Example: unique solution
    10x1 + 5x2 = 5
    4x2 + 3x3 = 10
    x1 + 6x3 = 12

Rules:

- Variable names: a letter or `_`, then letters, digits or `_` (`x`, `x1`, `price_2`).
- Variable order is the order of first appearance in the file.
- Coefficients can be integers or decimals, positive or negative:
  `3x`, `-2.5y`, `x` (means 1), `-x` (means -1), `3*x`.
- Spaces around operators are optional: `2x+3y=5` and `2x + 3y = 5` are the same.
- A space inside one term is rejected: `2 x`, `x y`, `0.75 z`.
- A variable missing from a line gets coefficient `0`.
- A repeated variable in one line is added together: `2x + 3x = 10` gives `5`.
- Blank lines and lines starting with `#` are skipped.
- Variables only on the left of `=`, and one number on the right.

A line is rejected with `InvalidFileFormatException` when it has no `=` or
more than one, an empty side, an unsupported character (brackets included),
two operators in a row, or a number with no variable on the left side.
The error message gives the real line number in the file, counting blank
lines and comments.

## Output format

Success:

    {
      "status": "SUCCESS",
      "system_info": {"num_variables": 3, "num_equations": 3},
      "solution": {"x1": 0.0, "x2": 1.0, "x3": 2.0}
    }

Error:

    {
      "status": "ERROR",
      "error_type": "InconsistentSystemException",
      "message": "The system has no solution (row reduces to 0 = 1)"
    }

Values are rounded to 4 decimal places, and `-0.0` is written as `0.0`.

## How the solver classifies a system

1. **Fewer equations than variables**: `DimensionMismatchException`,
   checked before elimination.
2. **Forward elimination** makes zeros below each pivot. If a pivot is
   zero, the row is swapped with a lower row that has a non-zero value
   in the same column.
3. **No solution**: after elimination, a row has all coefficients equal
   to zero but a non-zero constant (`0 = 1`). This raises
   `InconsistentSystemException`.
4. **Infinitely many solutions**: the number of pivots (the rank) is
   smaller than the number of variables, for example a row reduces to
   `0 = 0`. This raises `InfiniteSolutionsException`.
5. Otherwise the solution is unique and is found by **back substitution**.
   Extra equations that agree with the others are allowed.

Values smaller than `1e-9` are treated as zero, to avoid floating-point noise.

## Sample input files

| File | Result |
|---|---|
| `data/sample_success.txt` | x = 5, y = 3, z = -2 |
| `data/sample_invalid_format.txt` | InvalidFileFormatException |
| `data/sample_dimension_mismatch.txt` | DimensionMismatchException |
| `data/sample_no_solution.txt` | InconsistentSystemException |
| `data/sample_infinite_solutions.txt` | InfiniteSolutionsException |

To try one, copy it over `data/input_equations.txt` and run `py main.py`.

## Project layout

    pyeqsolver-project/
    ├── pyeqsolver/
    │   ├── __init__.py      exports EquationParser, GaussianSolver, JSONExporter
    │   ├── exceptions.py    PyEqSolverError and its 4 subclasses
    │   ├── parser.py        EquationParser
    │   ├── solver.py        GaussianSolver
    │   └── exporter.py      JSONExporter
    ├── tests/
    ├── data/
    ├── main.py
    └── README.md