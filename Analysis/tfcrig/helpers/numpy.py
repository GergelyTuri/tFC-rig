"""
Helper functions for working with NumPy data
"""
import warnings

import numpy as np

WARN_SCALAR_DIVIDE = [
    "invalid value encountered in scalar divide",
    "divide by zero encountered in scalar divide",
]


def scalar_divide(a: np.int64, b: np.int64) -> np.int64:
    """
    Divide two scalars, a numerator `a` and denominator `b`, without printing a
    `RuntimeWarning` if we divide by zero
    """
    with warnings.catch_warnings(record=True) as w:
        c = a / b

    if len(w) > 0:
        warning = w[0]
        if (
            not issubclass(warning.category, RuntimeWarning)
            or str(warning.message) not in WARN_SCALAR_DIVIDE
        ):
            # Raises an exception for other warnings
            raise Exception(warning.message)

    return c


def list_scalar_divide(l1: list[np.int64], l2: list[np.int64], c: np.int64=1):
    out = []
    with warnings.catch_warnings(record=True) as w:
        for a, b in zip(l1, l2):
            if b == 0:
                # Handle division by zero explicitly
                out.append(np.int64(0))
            else:
                out.append(c * a / b)
    if len(w) > 0:
        warning = w[0]
        if (
            not issubclass(warning.category, RuntimeWarning)
            or str(warning.message) not in WARN_SCALAR_DIVIDE
        ):
            # Raises an exception for other warnings
            raise Exception(warning.message)

    return out
