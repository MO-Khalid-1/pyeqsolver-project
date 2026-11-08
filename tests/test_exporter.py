import json
import os
import tempfile
import unittest

from pyeqsolver.exceptions import InconsistentSystemException
from pyeqsolver.exporter import JSONExporter


class TestJSONExporter(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "out", "solution.json")

    def tearDown(self):
        self.folder.cleanup()

    def read_json(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    def test_success_file(self):
        exporter = JSONExporter(self.path)
        exporter.save({"x": 1.0, "y": 2.0},
                      {"num_variables": 2, "num_equations": 2})
        self.assertEqual(self.read_json(), {
            "status": "SUCCESS",
            "system_info": {"num_variables": 2, "num_equations": 2},
            "solution": {"x": 1.0, "y": 2.0},
        })

    def test_values_are_rounded_to_4_places(self):
        JSONExporter(self.path).save({"x": 1 / 3, "y": 1.99999999},
                                     {"num_variables": 2, "num_equations": 2})
        solution = self.read_json()["solution"]
        self.assertEqual(solution, {"x": 0.3333, "y": 2.0})

    def test_negative_zero_becomes_zero(self):
        JSONExporter(self.path).save({"x": -0.00001},
                                     {"num_variables": 1, "num_equations": 1})
        with open(self.path, "r", encoding="utf-8") as file:
            text = file.read()
        self.assertNotIn("-0.0", text)

    def test_error_file(self):
        error = InconsistentSystemException("The system has no solution")
        JSONExporter(self.path).save_error(error)
        self.assertEqual(self.read_json(), {
            "status": "ERROR",
            "error_type": "InconsistentSystemException",
            "message": "The system has no solution",
        })

    def test_error_file_for_missing_input(self):
        JSONExporter(self.path).save_error(FileNotFoundError("missing.txt"))
        self.assertEqual(self.read_json()["error_type"], "FileNotFoundError")