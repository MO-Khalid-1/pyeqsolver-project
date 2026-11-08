import unittest

from pyeqsolver.exceptions import (
    DimensionMismatchException,
    InconsistentSystemException,
    InfiniteSolutionsException,
)
from pyeqsolver.solver import GaussianSolver


class TestSolverUniqueSolution(unittest.TestCase):

    def assert_solution(self, matrix, variables, expected):
        solution = GaussianSolver(matrix, variables).solve()
        self.assertEqual(list(solution), variables)
        for name in variables:
            self.assertAlmostEqual(solution[name], expected[name], places=6)

    def test_case_1(self):
        matrix = [[10, 5, 0, 5], [0, 4, 3, 10], [1, 0, 6, 12]]
        self.assert_solution(matrix, ["x1", "x2", "x3"],
                             {"x1": 0, "x2": 1, "x3": 2})

    def test_case_2_needs_row_swap(self):
        matrix = [[1, 1, 1, 6], [1, 1, 2, 9], [1, 2, 1, 8]]
        self.assert_solution(matrix, ["x", "y", "z"],
                             {"x": 1, "y": 2, "z": 3})

    def test_case_3_decimals(self):
        matrix = [[0.5, 1.5, 3.5], [2, -1, 0]]
        self.assert_solution(matrix, ["a", "b"], {"a": 1, "b": 2})

    def test_case_4_single_equation(self):
        self.assert_solution([[3, 1]], ["x"], {"x": 1 / 3})

    def test_case_5_repeated_variable(self):
        self.assert_solution([[5, 10]], ["x"], {"x": 2})

    def test_case_6_extra_consistent_equation(self):
        matrix = [[1, 1, 3], [1, -1, 1], [2, 2, 6]]
        self.assert_solution(matrix, ["x", "y"], {"x": 2, "y": 1})

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
            GaussianSolver([[1, 1, 2], [1, 1, 3]], ["x", "y"]).solve()

    def test_case_8_infinite_solutions(self):
        with self.assertRaises(InfiniteSolutionsException):
            GaussianSolver([[1, 1, 2], [2, 2, 4]], ["x", "y"]).solve()

    def test_case_9_fewer_equations(self):
        matrix = [[1, 1, 1, 1], [1, -1, 0, 0]]
        with self.assertRaises(DimensionMismatchException):
            GaussianSolver(matrix, ["x", "y", "z"]).solve()