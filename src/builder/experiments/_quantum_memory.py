"""A class to run quantum memory experiments."""

import stim

from typing import Literal, TypeAlias
from builder.experiments import Basis
from builder.experiments._experiment import Experiment
from builder.patches import RotatedSurfaceCode
from builder.utilities.grids import SquareGrid


class QuantumMemory(Experiment):
    def __init__(
        self,
        code_distance: tuple[int, int],
        logical_basis: Basis | list[Basis],
        num_qubits: int = 1,
    ):
        self._dx, self._dz = code_distance
        super().__init__(
            qubit_grid=SquareGrid(num_qubits * (self._dz + 1), self._dx + 1)
        )
        self.patches: list[RotatedSurfaceCode] = [
            RotatedSurfaceCode(
                code_distance=code_distance,
                qubit_grid=self.grid,
                anchor=(x * (self._dz + 1) + 1, 1),
            )
            for x in range(num_qubits)
        ]
        self.logical_basis = (
            logical_basis
            if isinstance(logical_basis, list)
            else [logical_basis] * num_qubits
        )
        if len(self.logical_basis) != num_qubits:
            raise ValueError(
                "Invalid inputs. If providing a list of logical bases, the length of the list must equal the number of logical qubits."
                + f"Received bases={self.logical_basis} and num_qubits={num_qubits}"
            )
        self.num_qubits = num_qubits

    def run(self, syndrome_extraction_rounds: int) -> stim.Circuit:
        self.initialize_patches(patches=self.patches, logical_bases=self.logical_basis)
        for _ in range(1, syndrome_extraction_rounds):
            self.syndrome_extraction_with_detectors(patches=self.patches)
        self.measure_patches(patches=self.patches, logical_bases=self.logical_basis)
        return self.circuit
