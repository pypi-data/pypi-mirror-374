# Copyright (c) 2025 LIN XIAO DAO
# Licensed under the MIT License. See LICENSE file in the project root for full license text.

import itertools
import numpy as np
from numpy.typing import NDArray

def full_counts(counts: dict[str, int], num_qubits: int) -> NDArray[np.int_]:
    """
    Construct a complete counts vector from measurement outcomes.

    This ensures that all basis states are represented, even if some
    outcomes are missing from the input dictionary. Missing outcomes
    are filled with zero counts.

    Parameters
    ----------
    counts : dict[str, int]
        Dictionary of measurement outcomes, where keys are bitstrings
        and values are counts.
    num_qubits : int
        The number of qubits in the quantum circuit.

    Returns
    -------
    NDArray of shape (2**num_qubits,)
        A vector containing counts for all basis states in lexicographic order.
    """
    all_bitstrings = ["".join(states) for states in itertools.product("01", repeat=num_qubits)]
    return np.array([counts.get(key, 0) for key in all_bitstrings])


def vector_MAE(vector1: NDArray[np.floating], vector2: NDArray[np.floating]) -> float:
    """
    Compute the mean absolute error (MAE) between two vectors.

    Parameters
    ----------
    vector1 : NDArray
        First vector for comparison.
    vector2 : NDArray
        Second vector for comparison.

    Returns
    -------
    float
        The mean absolute error between the two vectors.
    """
    return float(np.sum(np.abs(vector1 - vector2)) / vector1.size)
