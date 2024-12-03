"""A class to run quantum memory experiments."""

import matplotlib.figure
import stim

from builder.experiments import Basis
from builder.experiments._experiment import Experiment
from builder.patches import RotatedSurfaceCode
from builder.utilities.grids import SquareGrid


class QuantumMemory(Experiment):
    """A class for running quantum memory experiments. Multiple patches can be
    initialized at once and executed simultaneously.

    Parameters
    ----------
    code_distance: tuple[int, int]
        The code distance for each logical qubit, presented as a (dx, dz) tuple.
    logical_basis: Basis | list[Basis]
        String literal(s) for prepared qubit state(s). If only one Basis is provided,
        each logical qubit is prepared in that state. Otherwise, logical qubit i
        will be prepared in Basis at index i.
    num_qubits: int, optional
        The number of logical qubits to prepare, by default 1.

    Raises
    ------
    ValueError
        If a mismatch occurs between the required number of logical qubits, and the
        provided logical bases.

    Attributes
    ----------
    run
        Run the quantum memory experiment for the provided number of syndrome
        extraction rounds. A stim.Circuit object of the experiment is returned.
    """

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
                """Invalid inputs. If providing a list of logical bases, 
                the length of the list must equal the number of logical qubits."""
                + f"Received bases={self.logical_basis} and num_qubits={num_qubits}"
            )
        self.num_qubits = num_qubits

    def run(self, syndrome_extraction_rounds: int) -> stim.Circuit:
        """Run the quantum memory experiment for the provided number of syndrome
        extraction rounds.

        Parameters
        ----------
        syndrome_extraction_rounds : int
            The number of syndrome extraction rounds to evolve the qubits for.

        Returns
        -------
        stim.Circuit
        """
        self.initialize_patches(patches=self.patches, logical_bases=self.logical_basis)
        for _ in range(1, syndrome_extraction_rounds):
            self.syndrome_extraction_with_detectors(patches=self.patches)
        self.measure_patches(patches=self.patches, logical_bases=self.logical_basis)

        for observable_index, (patch, basis) in enumerate(
            zip(self.patches, self.logical_basis)
        ):
            observable_qubits = (
                patch.left_boundary_data if basis == "X" else patch.bottom_boundary_data
            )
            self.observable(
                observable_index=observable_index,
                targets=[self.measurement_record[qubit] for qubit in observable_qubits],
            )
        return self.circuit

    def draw(self) -> matplotlib.figure.Figure:
        """Draw the memory experiment.

        Returns
        -------
        matplotlib.figure.Figure
            A matplotlib figure.
        """
        vis = self._draw(patches=self.patches)
        return vis.figure
