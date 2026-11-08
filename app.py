"""Streamlit web page for PyEqSolver (for demo only)."""

import json
import os
import tempfile

import streamlit as st

from pyeqsolver import EquationParser, GaussianSolver, JSONExporter
from pyeqsolver.exceptions import PyEqSolverError

EXAMPLE = "10x1 + 5x2 = 5\n4x2 + 3x3 = 10\nx1 + 6x3 = 12"

st.title("PyEqSolver")
st.write("Solve a system of linear equations with Gaussian Elimination.")

text = st.text_area("Equations (one per line)", EXAMPLE, height=180)

if st.button("Solve"):
    with tempfile.TemporaryDirectory() as folder:
        input_path = os.path.join(folder, "equations.txt")
        output_path = os.path.join(folder, "solution.json")

        # The parser reads from a file, so save the text to a temporary file.
        with open(input_path, "w", encoding="utf-8") as file:
            file.write(text)

        exporter = JSONExporter(output_path)
        matrix = None

        try:
            matrix, variables = EquationParser(input_path).parse()
            solver = GaussianSolver(matrix, variables)
            solution = solver.solve()
            exporter.save(solution, solver.get_metadata())
        except PyEqSolverError as error:
            exporter.save_error(error)

        # Read back the same JSON that main.py would write.
        with open(output_path, "r", encoding="utf-8") as file:
            result = json.load(file)

    if result["status"] == "SUCCESS":
        st.success("Solved")
        for name, value in result["solution"].items():
            st.write(f"**{name}** = {value}")
    else:
        st.error(f"{result['error_type']}: {result['message']}")

    if matrix is not None:
        st.subheader("Augmented matrix [A | b]")
        st.table([dict(zip(variables + ["b"], row)) for row in matrix])

    st.subheader("JSON output")
    st.code(json.dumps(result, indent=2), language="json")