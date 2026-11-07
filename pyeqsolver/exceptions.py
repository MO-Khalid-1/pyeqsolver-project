"""
Project exceptions.

All of them inherit from PyEqSolverError.

FileNotFoundError is not defined here: it is a built-in Python exception.
"""

class PyEqSolverError(Exception):
    """Base class for all errors in this project."""


class InvalidFileFormatException(PyEqSolverError):
    """The input file has a bad format."""


class DimensionMismatchException(PyEqSolverError):
    """Fewer equations than variables."""


class InconsistentSystemException(PyEqSolverError):
    """The system has no solution."""


class InfiniteSolutionsException(PyEqSolverError):
    """The system has infinitely many solutions."""