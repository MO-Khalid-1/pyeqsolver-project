"""Solve a linear system with Gaussian Elimination."""

from pyeqsolver.exceptions import (
    DimensionMismatchException,
    InconsistentSystemException,
    InfiniteSolutionsException,
)

# Values smaller than this are treated as zero (floating-point noise).
EPSILON = 1e-9


class GaussianSolver:
    """Solve the augmented matrix [A | b] produced by EquationParser."""

    def __init__(self, matrix: list[list[float]], variables: list[str]) -> None:
        """Store a copy of the matrix and the variable names."""
        # Copy every row, so the caller's matrix is never changed.
        self.matrix = [row[:] for row in matrix]
        self.variables = list(variables)
        self.num_equations = len(matrix)
        self.num_variables = len(variables)

    def solve(self) -> dict[str, float]:
        """Return {variable: value}, or raise if there is no unique solution."""
        if self.num_equations < self.num_variables:
            names = ", ".join(self.variables)
            raise DimensionMismatchException(
                f"{self.num_equations} equations for "
                f"{self.num_variables} variables ({names})"
            )

        rank = self._forward_eliminate()
        self._check_consistency(rank)

        if rank < self.num_variables:
            raise InfiniteSolutionsException(
                f"Infinitely many solutions: rank {rank} < "
                f"{self.num_variables} variables"
            )

        values = self._back_substitute()
        return dict(zip(self.variables, values))

    def get_metadata(self) -> dict:
        """Return the number of variables and equations."""
        return {
            "num_variables": self.num_variables,
            "num_equations": self.num_equations,
        }

    def _forward_eliminate(self) -> int:
        """Make zeros below every pivot and return the rank."""
        pivot_row = 0

        for col in range(self.num_variables):
            if pivot_row == self.num_equations:
                break

            found = None
            for row in range(pivot_row, self.num_equations):
                if abs(self.matrix[row][col]) > EPSILON:
                    found = row
                    break

            if found is None:
                continue

            # Row swap (mandatory pivoting).
            if found != pivot_row:
                self.matrix[pivot_row], self.matrix[found] = (
                    self.matrix[found], self.matrix[pivot_row]
                )

            pivot = self.matrix[pivot_row][col]

            for row in range(pivot_row + 1, self.num_equations):
                factor = self.matrix[row][col] / pivot
                if factor == 0:
                    continue
                # R2 = R2 - factor * R1, including the constant
                for j in range(col, self.num_variables + 1):
                    self.matrix[row][j] -= factor * self.matrix[pivot_row][j]

            pivot_row += 1

        return pivot_row

    def _check_consistency(self, rank: int) -> None:
        """Raise if a row reduced to 0 = c with c not zero."""
        for row in self.matrix[rank:]:
            constant = row[-1]
            if abs(constant) > EPSILON:
                raise InconsistentSystemException(
                    f"The system has no solution (row reduces to 0 = {constant:g})"
                )

    def _back_substitute(self) -> list[float]:
        """Solve from the last pivot row up to the first one."""
        n = self.num_variables
        values = [0.0] * n

        for i in range(n - 1, -1, -1):
            total = self.matrix[i][n]
            for j in range(i + 1, n):
                total -= self.matrix[i][j] * values[j]
            values[i] = total / self.matrix[i][i]

        return values