"""Read and parse linear equations into an augmented matrix."""

import re

from pyeqsolver.exceptions import InvalidFileFormatException

_BRACKET_RE = re.compile(r"[(){}\[\]]")
_LEFT_VALID_CHARS_RE = re.compile(r"^[\w\s+\-*.]+$")
_CONSECUTIVE_OPERATORS_RE = re.compile(r"[+\-]\s*[+\-]")
_NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")
_SPACE_RE = re.compile(r"\s+")
_SPLIT_TERM_RE = re.compile(r"[\w.]\s+[\w.]")
_SPACE_RE = re.compile(r"\s+")
_TERM_RE = re.compile(
    r"([+\-])((?:\d+(?:\.\d*)?|\.\d+)\*?)?([a-zA-Z_]\w*)"
)


class EquationParser:
    """Read equations from a text file and convert them to an augmented matrix."""

    def __init__(self, file_path: str) -> None:
        """Store the path of the input file."""
        self.file_path = file_path

    def parse(self) -> tuple[list[list[float]], list[str]]:
        """Read the file and return the augmented matrix and variable names."""
        equations = self._read_equations()

        if not equations:
            raise InvalidFileFormatException(
                "The file contains no equations."
            )

        variables = []
        parsed = []

        for line_number, line in equations:
            coefficients, constant = self._parse_line(line, line_number)

            for variable in coefficients:
                if variable not in variables:
                    variables.append(variable)

            parsed.append((coefficients, constant))

        matrix = []
        for coefficients, constant in parsed:
            row = [coefficients.get(variable, 0.0) for variable in variables]
            row.append(constant)
            matrix.append(row)

        return matrix, variables

    def _read_equations(self) -> list[tuple[int, str]]:
        """Read non-empty, non-comment lines with their original line numbers."""
        equations = []

        with open(self.file_path, "r", encoding="utf-8-sig") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                equations.append((line_number, line))

        return equations

    def _split_equation(self, line: str, line_number: int) -> tuple[str, str]:
        """Split one equation into its left-hand and right-hand sides."""
        if line.count("=") != 1:
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "Expected exactly one '=' sign."
            )

        left, right = line.split("=")
        left = left.strip()
        right = right.strip()

        if not left or not right:
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "Both sides must contain values."
            )

        return left, right

    def _parse_line(
        self, line: str, line_number: int
    ) -> tuple[dict[str, float], float]:
        """Parse one equation into {variable: coefficient} and the constant."""

        left, right = self._split_equation(line, line_number)

        if _BRACKET_RE.search(left):
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "Brackets are not supported."
            )

        if not _LEFT_VALID_CHARS_RE.fullmatch(left):
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "The left-hand side contains invalid characters."
            )

        if _CONSECUTIVE_OPERATORS_RE.search(left):
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "Consecutive '+' or '-' operators are not allowed."
            )

        if _CONSECUTIVE_OPERATORS_RE.search(left):
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "Consecutive '+' or '-' operators are not allowed."
            )

        if _SPLIT_TERM_RE.search(left):
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "Spaces are not allowed inside a term."
            )

        if not _NUMBER_RE.fullmatch(right):
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "The right-hand side must be a single integer or decimal number."
            )

        right_value = float(right)

        expression = _SPACE_RE.sub("", left)

        if expression[0] not in "+-":
            expression = "+" + expression

        coefficients = {}
        position = 0

        for match in _TERM_RE.finditer(expression):

            if match.start() != position:
                raise InvalidFileFormatException(
                    f"Invalid equation at line {line_number}: {line!r}. "
                    "Invalid term in the left-hand side."
                )

            sign, coefficient_text, variable = match.groups()

            if coefficient_text is None:
                coefficient = 1.0
            else:
                coefficient = float(coefficient_text.rstrip("*"))

            if sign == "-":
                coefficient = -coefficient

            coefficients[variable] = (
                coefficients.get(variable, 0.0) + coefficient
            )

            position = match.end()

        if position != len(expression) or not coefficients:
            raise InvalidFileFormatException(
                f"Invalid equation at line {line_number}: {line!r}. "
                "Invalid or missing variable term in the left-hand side."
            )

        return coefficients, right_value