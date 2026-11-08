"""Streamlit web page for PyEqSolver (for demo only)."""

import os
import tempfile

import streamlit as st

from pyeqsolver import EquationParser, GaussianSolver
from pyeqsolver.exceptions import PyEqSolverError

EXAMPLE = "10x1 + 5x2 = 5\n4x2 + 3x3 = 10\nx1 + 6x3 = 12"

st.title("PyEqSolver")
st.write("Solve a system of linear equations with Gaussian Elimination.")

text = st.text_area("Equations (one per line)", EXAMPLE, height=180)

if st.button("Solve"):
    # The parser reads from a file, so save the text to a temporary file.
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "equations.txt")
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

        try:
            matrix, variables = EquationParser(path).parse()
            solution = GaussianSolver(matrix, variables).solve()
        except PyEqSolverError as error:
            st.error(f"{type(error).__name__}: {error}")
        else:
            st.success("Solved")
            for name, value in solution.items():
                value = round(value, 4)
                if value == 0:
                    value = 0.0
                st.write(f"**{name}** = {value}")

            st.subheader("Augmented matrix [A | b]")
            st.table([dict(zip(variables + ["b"], row)) for row in matrix])