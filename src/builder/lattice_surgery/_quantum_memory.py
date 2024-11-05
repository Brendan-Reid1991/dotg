"""Quantum memory experiments over N qubits."""

from typing import Literal
import matplotlib.pyplot as plt
import matplotlib
import stim
from builder.lattice_surgery._experiment import LatticeSurgeryExperiment
from builder.patches import RotatedSurfaceCode
from builder.utilities.grids import SquareGrid
from builder.utilities import Visualiser

from dotg.utilities.stim_assets import ResetGates, MeasurementGates

Basis = Literal["X", "Z"]


class QuantumMemory(LatticeSurgeryExperiment):
    """A class for running quantum memory experiments on N qubits.

    Parameters
    ----------
    code_distance : tuple[int, int]
        (X, Z) tuple describing the code distances.
    num_qubits : int
        Number of individual logical qubits to simulate.
    basis : Basis
        Which basis to prepare the qubits in.
    """

    def __init__(
        self, code_distance: tuple[int, int], num_qubits: int, bases: list[Basis] | Basis
    ):
        self.num_qubits = num_qubits
        _rows, _columns = code_distance
        self.code_distance = code_distance
        if len(bases) != self.num_qubits and len(bases) != 1:
            raise ValueError(
                "Must supply either a base for all logical qubits or a base for each."
            )
        self.bases = bases if len(bases) == self.num_qubits else bases * self.num_qubits

        super().__init__(SquareGrid(self.num_qubits * (_columns + 1) + 1, _rows + 1))

        self.patches: list[RotatedSurfaceCode] = [
            RotatedSurfaceCode(
                code_distance=self.code_distance,
                qubit_grid=self.grid,
                anchor=(x * (_columns + 1) + 1, 1),
            )
            for x in range(num_qubits)
        ]

    def prepare_qubits(self):
        """Prepare the logical qubit states."""
        for patch, basis in zip(self.patches, self.bases):
            self.reset_qubits(
                patch.data_qubits,
                ResetGates.RZ if basis == "Z" else ResetGates.RX,
            )
            self.reset_qubits(patch.z_stabilizers, ResetGates.RZ)
            self.reset_qubits(patch.x_stabilizers, ResetGates.RX)

        self.tick()

        self._depth_4_syndrome_extraction(patches=self.patches)

        for patch, basis in zip(self.patches, self.bases):
            self.measure_qubits(qubits=patch.z_stabilizers, basis=MeasurementGates.MZ)
            self.detector_batch(
                patch.z_stabilizers,
                new_measurements_deterministic=(basis == "Z"),
            )
            self.measure_qubits(qubits=patch.x_stabilizers, basis=MeasurementGates.MX)
            self.detector_batch(
                patch.x_stabilizers,
                new_measurements_deterministic=(basis == "X"),
            )
        self.timeshift()
        self.tick()

    def syndrome_extraction(self, rounds: int):
        """Perform syndrome extraction for a number of rounds on the
        logical qubits.

        Parameters
        ----------
        rounds : int
            Number of rounds of syndrome extraction to perform.
        """
        for _ in range(rounds):
            for patch in self.patches:
                self.reset_qubits(patch.z_stabilizers, ResetGates.RZ)
                self.reset_qubits(patch.x_stabilizers, ResetGates.RX)
            self.tick()
            self.syndrome_extraction_with_detectors(patches=self.patches)
            self.timeshift()
            self.tick()

    def measure_states(self):
        """Measure the states of the logical qubits."""
        for patch, basis in zip(self.patches, self.bases):
            gate = MeasurementGates.MZ if basis == "Z" else MeasurementGates.MX
            self.measure_qubits(patch.data_qubits, gate)
            self._increment_measurement_record(patch.data_qubits)
            stabilizers = (
                patch.z_stabilizers
                if gate is MeasurementGates.MZ
                else patch.x_stabilizers
            )
            self.detector_batch_with_data_qubits(
                stabilizers=stabilizers,
                data_qubit_member_check=patch.data_qubits,
                final_round_detector=True,
            )

    def add_observables(self):
        """Add observables for each qubit."""
        for patch, basis in zip(self.patches, self.bases):
            if basis == "Z":
                self.observable(
                    self.patches.index(patch),
                    [self.measurement_record[q] for q in patch.bottom_boundary_data],
                )
            else:
                self.observable(
                    self.patches.index(patch),
                    [self.measurement_record[q] for q in patch.left_boundary_data],
                )

    def run_experiment(self, memory_rounds: int) -> stim.Circuit:
        """Return the circuit describing the quantum memory experiment.

        Parameters
        ----------
        memory_rounds : int
            Number of rounds of syndrome extraction to perform.
        """
        self.prepare_qubits()
        self.syndrome_extraction(rounds=memory_rounds - 1)
        self.measure_states()
        self.add_observables()
        return self.circuit

    def draw(
        self,
        figure_size: tuple[int, int] = (20, 10),
        indices: bool = True,
        highlight_logicals: bool = False,
    ) -> matplotlib.figure.Figure:
        """Draw the experiment. Returns a matplotlib figure.

        Parameters
        ----------
        indices : bool, optional
            Whether or not to add indices to the diagram, by default True.
        highlight_logicals : bool, optional
            Whether or not to highlight the logicals, by default False.

        Returns
        -------
        matplotlib.figure.Figure
        """
        vis = Visualiser(grid=self.grid, show_indices=indices, figsize=figure_size)

        for patch in self.patches:
            for qubit in patch.data_qubits:
                vis.draw_qubit(qubit=qubit)
            for stabilizer in patch.x_stabilizers:
                vis.draw_stabilizer(
                    stabilizer=stabilizer,
                    color="red",
                    data_qubit_member_check=patch.data_qubits,
                )
            for stabilizer in patch.z_stabilizers:
                vis.draw_stabilizer(
                    stabilizer=stabilizer,
                    color="blue",
                    data_qubit_member_check=patch.data_qubits,
                )
        return vis.figure
