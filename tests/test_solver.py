import unittest

from pyeqsolver.exceptions import (
    DimensionMismatchException,
    InconsistentSystemException,
    InfiniteSolutionsException,
)
from pyeqsolver.parser import EquationParser
from pyeqsolver.solver import GaussianSolver


def solve_case(name):
    """Read a test file from tests/data and solve it."""
    matrix, variables = EquationParser(f"tests/data/{name}").parse()
    return GaussianSolver(matrix, variables).solve()


class TestSolverUniqueSolution(unittest.TestCase):

    def assert_solution(self, name, expected):
        solution = solve_case(name)
        self.assertEqual(list(solution), list(expected))
        for variable, value in expected.items():
            self.assertAlmostEqual(solution[variable], value, places=4)

    def test_case_1(self):
        self.assert_solution("case01.txt", {"x1": 0, "x2": 1, "x3": 2})

    def test_case_2_needs_row_swap(self):
        self.assert_solution("case02.txt", {"x": 1, "y": 2, "z": 3})

    def test_case_3_decimals(self):
        self.assert_solution("case03.txt", {"a": 1, "b": 2})

    def test_case_4_single_equation(self):
        self.assert_solution("case04.txt", {"x": 0.3333})

    def test_case_5_repeated_variable(self):
        self.assert_solution("case05.txt", {"x": 2})

    def test_case_6_extra_consistent_equation(self):
        self.assert_solution("case06.txt", {"x": 2, "y": 1})

    def test_original_matrix_is_not_changed(self):
        matrix = [[1, 1, 1, 6], [1, 1, 2, 9], [1, 2, 1, 8]]
        copy = [row[:] for row in matrix]
        GaussianSolver(matrix, ["x", "y", "z"]).solve()
        self.assertEqual(matrix, copy)

    def test_metadata(self):
        solver = GaussianSolver([[1, 1, 3], [1, -1, 1], [2, 2, 6]], ["x", "y"])
        self.assertEqual(
            solver.get_metadata(),
            {"num_variables": 2, "num_equations": 3},
        )


class TestSolverErrors(unittest.TestCase):

    def test_case_7_no_solution(self):
        with self.assertRaises(InconsistentSystemException):
            solve_case("case07.txt")

    def test_case_8_infinite_solutions(self):
        with self.assertRaises(InfiniteSolutionsException):
            solve_case("case08.txt")

    def test_case_9_fewer_equations(self):
        with self.assertRaises(DimensionMismatchException):
            solve_case("case09.txt")