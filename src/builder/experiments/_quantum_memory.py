"""A class to run quantum memory experiments."""

from typing import Literal, TypeAlias
from builder.experiments import Basis
from builder.experiments._experiment import Experiment
from builder.utilities.grids import SquareGrid


class QuantumMemory(Experiment):
    def __init__(
        self,
        code_distance: int | tuple[int, int],
        logical_basis: Basis | list[Basis],
        qubit_grid: SquareGrid,
        num_qubits: int = 1,
    ):
        super().__init__(qubit_grid=qubit_grid)
        self.logical_basis = logical_basis
        self.num_qubits = num_qubits
        if isinstance(self.logical_basis, list):
            if len(self.logical_basis) != num_qubits:
                raise ValueError(
                    "Invalid inputs. If providing a list of logical bases, the length of the list must equal the number of logical qubits."
                    + f"Received bases={self.logical_basis} and num_qubits={self.num_qubits}"
                )

    def run(self, syndrome_extraction_rounds: int)