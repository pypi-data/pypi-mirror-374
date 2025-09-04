# Copyright (c) 2025 LIN XIAO DAO
# Licensed under the MIT License. See LICENSE file in the project root for full license text.

from __future__ import annotations

from typing import Any, Optional

import numpy as np
from numpy.typing import NDArray
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_ibm_runtime.fake_provider import (
    FakeLimaV2,
    FakeBrisbane,
    FakeSherbrooke,
    FakeAthensV2,
)

from .models import Autoencoder
from .utils import full_counts, vector_MAE
from .plot_utils import OverallPlot


class JobCenter:
    """
    A small controller that runs 4-qubit mitigation jobs and visualizes results.

    Notes
    -----
    This implementation is **specialized for 4-qubit circuits**.
    The underlying autoencoder expects 16-dimensional probability
    vectors (input/output) and cannot be applied to other sizes.

    Attributes
    ----------
    AE : keras.Model
        The pretrained autoencoder model used for mitigation.
    backends : dict[str, Any]
        Available fake backends for users to select.
    jobs : dict[str, dict[str, Any]]
        Storage for job artifacts and results keyed by ``job_id``.
    """

    def __init__(self, checkpoint_name: str = "F") -> None:
        """Initialize the controller with the autoencoder and available backends."""
        self.AE = Autoencoder()
        self.backends: dict[str, Any] = {
            "FakeLima": FakeLimaV2(),
            "FakeAthens": FakeAthensV2(),
            "FakeBrisbane": FakeBrisbane(),
            "FakeSherbrooke": FakeSherbrooke(),
        }
        self.jobs: dict[str, dict[str, Any]] = {}

    def add_job(
        self,
        circ: QuantumCircuit,
        job_id: str,
        backend_name: Optional[str] = None,
        shots: int = 1e4,
    ) -> None:
        """
        Add a new job and perform mitigation (restricted to 4-qubit circuits).

        Parameters
        ----------
        circ : QuantumCircuit
            A 4-qubit quantum circuit to be executed.
        job_id : str
            Identifier string for the job.
        backend_name : str, optional
            Backend name chosen from the available backend dictionary.
            If ``None`` or empty, defaults to ``"FakeLima"``.
        shots : int, default=10000
            Number of measurement shots.

        Raises
        ------
        ValueError
            If the circuit does not have exactly 4 qubits.
        TypeError
            If argument types are invalid.
        KeyError
            If the given backend name is not available.
        """
        if not isinstance(circ, QuantumCircuit):
            raise TypeError("`circ` must be a qiskit.QuantumCircuit instance.")
        if not isinstance(job_id, str):
            raise TypeError("`job_id` must be a string.")
        if backend_name is None or backend_name == "":
            backend_name = "FakeLima"
        if not isinstance(backend_name, str):
            raise TypeError("`backend_name` must be a string.")
        if backend_name not in self.backends:
            raise KeyError(
                f"Backend '{backend_name}' is not available. "
                f"Available: {list(self.backends.keys())}"
            )

        if circ.num_qubits != 4:
            raise ValueError(
                f"This autoencoder only supports 4-qubit circuits; got {circ.num_qubits}."
            )

        backend = self.backends[backend_name]

        # Build reference (statevector) probabilities.
        circ = circ.copy()
        circ.remove_final_measurements()
        theorem: NDArray[np.floating] = Statevector.from_instruction(circ).probabilities()

        # Execute noisy measurement on the selected backend.
        circ.measure_all()
        counts = backend.run(circ, shots=shots).result().get_counts()
        noise_vec = full_counts(counts=counts, num_qubits=4).astype(float) / shots  # (16,)
        # Mitigate by our autoencoder model.
        miti_vec: NDArray[np.floating] = self.AE.mitigate(noise_vec[np.newaxis, :]).flatten()
        # Store artifacts/results.
        self.jobs[job_id] = {
            "circuit": circ,
            "backend": backend_name,
            "Statevector": theorem,     # (16,)
            "noisy_input": noise_vec,   # (16,)
            "Autoencoder": miti_vec,    # (16,)
        }

    def visualization(self, job_id: str) -> None:
        """
        Visualize a job's measurement outcomes as bar plots.

        Parameters
        ----------
        job_id : str
            The job identifier to visualize.

        Raises
        ------
        KeyError
            If the job ID is not found in storage.
        """
        if job_id not in self.jobs:
            raise KeyError(
                f"Job id '{job_id}' not found. Existing: {list(self.jobs.keys())}"
            )
        plotter = OverallPlot(self.jobs[job_id])    
        plotter.plot_result()
