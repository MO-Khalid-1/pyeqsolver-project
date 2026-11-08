import os
import tempfile
import unittest

from pyeqsolver.exceptions import InvalidFileFormatException
from pyeqsolver.parser import EquationParser


def parse_case(name):
    return EquationParser(f"tests/data/{name}").parse()


def parse_text(text):
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "eq.txt")
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        return EquationParser(path).parse()


class TestParserValidInput(unittest.TestCase):

    def test_case_1_matrix(self):
        parser = EquationParser("tests/data/case01.txt")
        matrix, variables = parser.parse()
        self.assertEqual(matrix, [
            [10.0, 5.0, 0.0, 5.0],
            [0.0, 4.0, 3.0, 10.0],
            [1.0, 0.0, 6.0, 12.0],
        ])

    def test_case_1_variables(self):
        parser = EquationParser("tests/data/case01.txt")
        matrix, variables = parser.parse()
        self.assertEqual(variables, ["x1", "x2", "x3"])


class TestParserMoreValidCases(unittest.TestCase):

    def test_case_2_three_variables(self):
        matrix, variables = parse_case("case02.txt")
        self.assertEqual(matrix, [
            [1.0, 1.0, 1.0, 6.0],
            [1.0, 1.0, 2.0, 9.0],
            [1.0, 2.0, 1.0, 8.0],
        ])
        self.assertEqual(variables, ["x", "y", "z"])

    def test_case_3_decimals(self):
        matrix, variables = parse_case("case03.txt")
        self.assertEqual(matrix, [[0.5, 1.5, 3.5], [2.0, -1.0, 0.0]])
        self.assertEqual(variables, ["a", "b"])

    def test_case_4_single_equation(self):
        matrix, variables = parse_case("case04.txt")
        self.assertEqual(matrix, [[3.0, 1.0]])
        self.assertEqual(variables, ["x"])

    def test_case_5_repeated_variable(self):
        matrix, variables = parse_case("case05.txt")
        self.assertEqual(matrix, [[5.0, 10.0]])

    def test_case_6_extra_equation(self):
        matrix, variables = parse_case("case06.txt")
        self.assertEqual(matrix, [
            [1.0, 1.0, 3.0],
            [1.0, -1.0, 1.0],
            [2.0, 2.0, 6.0],
        ])

    def test_extra_valid_example(self):
        matrix, variables = parse_case("extra_valid.txt")
        self.assertEqual(matrix, [
            [1.0, 1.0, 1.0, 6.0],
            [0.0, 2.0, 5.0, -4.0],
            [2.0, 5.0, -1.0, 27.0],
        ])
        self.assertEqual(variables, ["x", "y", "z"])

    def test_parser_does_not_judge_solvability(self):
        # case07 has no solution, but the parser only builds the matrix.
        matrix, variables = parse_case("case07.txt")
        self.assertEqual(matrix, [[1.0, 1.0, 2.0], [1.0, 1.0, 3.0]])


class TestParserErrors(unittest.TestCase):

    def test_missing_file(self):
        parser = EquationParser("tests/data/does_not_exist.txt")
        with self.assertRaises(FileNotFoundError):
            parser.parse()

    def test_case_10_missing_equal_sign(self):
        with self.assertRaises(InvalidFileFormatException) as context:
            parse_case("case10.txt")
        self.assertIn("line 1", str(context.exception))

    def test_case_11_brackets(self):
        with self.assertRaises(InvalidFileFormatException):
            parse_case("case11.txt")

    def test_case_12_empty_file(self):
        with self.assertRaises(InvalidFileFormatException):
            parse_case("case12_empty.txt")

    def test_case_12_only_comments(self):
        with self.assertRaises(InvalidFileFormatException):
            parse_case("case12_comments.txt")

    def test_error_uses_physical_line_number(self):
        with self.assertRaises(InvalidFileFormatException) as context:
            parse_text("# comment\n\n2x + 3y 7\n")
        self.assertIn("line 3", str(context.exception))


class TestParserSpaces(unittest.TestCase):

    def test_space_inside_term_is_rejected(self):
        for text in ["2 x + y = 3", "x y = 3", "x 2 = 3"]:
            with self.subTest(text=text):
                with self.assertRaises(InvalidFileFormatException):
                    parse_text(text)

    def test_space_around_operators_is_allowed(self):
        matrix, variables = parse_text("- x + 2 * y = 3")
        self.assertEqual(matrix, [[-1.0, 2.0, 3.0]])
        self.assertEqual(variables, ["x", "y"])