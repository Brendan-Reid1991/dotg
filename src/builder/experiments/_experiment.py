"""A helper class for running simulations."""

from __future__ import annotations
from typing import Optional, Callable, Any, Protocol
from mypy_extensions import NamedArg
import stim

from builder.experiments import Basis
from builder.patches import RotatedSurfaceCode
from builder.utilities import QubitCoordinate, Visualiser
from builder.utilities.grids import SquareGrid


from dotg.utilities.stim_assets import (
    StimAnnotations,
    ResetGates,
    MeasurementGates,
    TwoQubitGates,
    OneQubitGates,
)

# pylint: disable=protected-access


class CircuitModificationMethod(Protocol):
    def __call__(self, qubits: list[QubitCoordinate], **kwargs): ...


class Experiment:
    """A helper class for streamlining common aspects of experiments,
    such as syndrome extraction circuits and detector definitions.

    This class will generate a stim.Circuit object that defines
    the experiment.

    Parameters
    ----------
    qubit_grid: SquareGrid
        The grid the experiment will take place on. At present,
        only SquareGrid is permitted.

    Attributes
    ----------
    circuit: stim.Circuit
        The stim circuit object representing the experiment.
    measurement_record: Dict[QubitCoordinate, int]
        A dictionary of the most recent measurement performed on
        a qubit.
    """

    def __init__(self, qubit_grid: SquareGrid):
        self.grid = qubit_grid

        self.circuit: stim.Circuit = stim.Circuit()
        for qubit, idx in self.grid.coordinate_mapping.items():
            self.circuit.append(
                name=StimAnnotations.QUBIT_COORDS, arg=qubit, targets=idx
            )

        self.measurement_record: dict[QubitCoordinate, int] = {}

    def confirm_valid_qubits(circuit_modifier: CircuitModificationMethod):
        def wrapper(self: Experiment, *args, **kwargs):
            if not all(isinstance(q, QubitCoordinate) for q in kwargs["qubits"]):
                raise ValueError(
                    f"""Some qubits provided to {circuit_modifier.__name__} are not 
                    QubitCoordinate objects, and therefore will not have indices. 
                    Qubits are required to have defined indices for simulation in 
                    stim."""
                )
            if not any(q.idx for q in kwargs["qubits"]):
                raise ValueError("QubitCoordinate index is not defined!")
            if len(set(q.idx for q in kwargs["qubits"])) != len(kwargs["qubits"]):
                raise ValueError(
                    f"""Some qubits provided to {circuit_modifier.__name__} have the 
                    same indices; Qubits must have unique indices to be effectively 
                    added to a circuit."""
                )
            return circuit_modifier(self, *args, **kwargs)

        return wrapper

    def _increment_measurement_record(self, batch: list[QubitCoordinate]):
        """Increment the measurement record given the latest batch of measurements.

        Parameters
        ----------
        batch : List[QubitCoordinate]
            The qubits that have just been measured.
        """
        lookback = len(batch)
        for idx, qubit in enumerate(batch):
            self.measurement_record[qubit] = -lookback + idx
        for _index, _record in self.measurement_record.items():
            if _index in batch:
                continue
            self.measurement_record[_index] = _record - lookback

    def tick(self):
        """Add a tick to the stim circuit, finishing a timeslice."""
        self.circuit.append(StimAnnotations.TICK)

    def timeshift(self):
        """Increment the timelike entry of all detectors by 1."""
        self.circuit.append(StimAnnotations.SHIFT_COORDS, arg=[0, 0, 1])

    @confirm_valid_qubits
    # @check_qubit_coordinate_validity
    def reset_qubits(self, *, qubits: list[QubitCoordinate], basis: ResetGates):
        """Write a line to the stim circuit, resetting
        a list of qubits in the specified basis.

        Parameters
        ----------
        qubits : List[QubitCoordinate]
            List of qubits to reset.
        basis : ResetGates
            Which basis to reset the qubits into.
        """
        if basis not in ResetGates:
            raise ValueError(f"Invalid reset operation. Received {basis}.")
        self.circuit.append(name=basis, targets=[q.idx for q in qubits])

    # @check_qubit_coordinate_validity
    @confirm_valid_qubits
    def measure_qubits(
        self, *, qubits: list[QubitCoordinate], basis: MeasurementGates
    ) -> None:
        """Write a line to the stim circuit, measuring
        a list of qubits in the specified basis.

        Parameters
        ----------
        qubits : List[QubitCoordinate]
            List of qubits to measure.
        basis : MeasurementGates
            Which basis to measure the qubits in.
        """
        if basis not in MeasurementGates:
            raise ValueError(f"Invalid measurement operation. Received {basis}.")

        self.circuit.append(name=basis, targets=[q.idx for q in qubits])

    def initialize_patches(
        self, patches: list[RotatedSurfaceCode], logical_bases: list[Basis]
    ) -> None:
        """Initialize patches by resetting all data and stabilizer qubits,
        running a single round of syndrome extraction and measuring the stabilizer
        qubits to complete encoding.

        Parameters
        ----------
        patches : list[RotatedSurfaceCode]
            A list of rotated surface code patches.
        logical_bases : list[Basis]
            A list of logical states to encode in each logical qubit.
        """
        for patch, basis in zip(patches, logical_bases):
            self.reset_qubits(
                qubits=patch.data_qubits,
                basis=ResetGates.RX if basis == "X" else ResetGates.RZ,
            )
            self.reset_qubits(qubits=patch.x_stabilizers, basis=ResetGates.RX)
            self.reset_qubits(qubits=patch.z_stabilizers, basis=ResetGates.RZ)
        self.tick()
        self._depth_4_syndrome_extraction(patches=patches)
        for patch, basis in zip(patches, logical_bases):
            self.measure_qubits(qubits=patch.x_stabilizers, basis=MeasurementGates.MX)
            self.detector_batch(patch.x_stabilizers, basis == "X")
            self.measure_qubits(qubits=patch.z_stabilizers, basis=MeasurementGates.MZ)
            self.detector_batch(patch.z_stabilizers, basis == "Z")
        self.tick()
        self.timeshift()

    def measure_patches(
        self, patches: list[RotatedSurfaceCode], logical_bases: list[Basis]
    ) -> None:
        """Destructively measure the data qubits in each provided patch, in the
        corresponding basis.

        Parameters
        ----------
        patches : list[RotatedSurfaceCode]
            A list of rotated surface code patches.
        logical_bases : list[Basis]
            A list of logical bases to measure the logical qubits in.
        """
        for patch, basis in zip(patches, logical_bases):
            self.measure_qubits(
                qubits=patch.data_qubits,
                basis=MeasurementGates.MX if basis == "X" else MeasurementGates.MZ,
            )
            self._increment_measurement_record(batch=patch.data_qubits)
            self.detector_batch_with_data_qubits(
                stabilizers=patch.x_stabilizers if basis == "X" else patch.z_stabilizers,
                data_qubit_member_check=patch.data_qubits,
                final_round_detector=True,
            )

    # @check_qubit_coordinate_validity
    @confirm_valid_qubits
    def apply_gate(
        self, *, qubits: list[QubitCoordinate], gate: OneQubitGates | TwoQubitGates
    ):
        """Add a gate operation to the circuit.

        Parameters
        ----------
        qubits : list[QubitCoordinate]
            The target qubits for the gate.
        gate : OneQubitGates | TwoQubitGates
            The quantum gate operation.

        Raises
        ------
        ValueError
            If the gate is not a one- or two-qubit gate.
        """
        if all(
            gate not in quantum_ops for quantum_ops in [OneQubitGates, TwoQubitGates]
        ):
            raise ValueError(f"Invalid gate operation. Received {gate}.")

        self.circuit.append(gate, targets=[q.idx for q in qubits])

    def detector(self, qubit: QubitCoordinate, targets: list[int] | int):
        """Add a detector to the stim circuit.

        Parameters
        ----------
        qubit : QubitCoordinate
            Which qubit involved in this detector. This is used for the labelling.
        targets : List[int]
            A list of lookback integers for the measurement record.
        """
        targets = [targets] if isinstance(targets, int) else targets
        self.circuit.append(
            StimAnnotations.DETECTOR,
            arg=list(qubit) + [0],
            targets=map(stim.target_rec, targets),
        )

    def observable(self, observable_index: int, targets: list[int]):
        """Add an observable to the circuit.

        TODO Add automatic tracking by evolving PauliProducts.

        Parameters
        ----------
        observable_index : int
            Observable index, for labelling.
        targets : List[int]
            List of measurement records to include in the observable.
        """
        self.circuit.append(
            StimAnnotations.OBSERVABLE_INCLUDE,
            arg=observable_index,
            targets=map(stim.target_rec, targets),
        )

    def _syndrome_extraction_circuit_entries(
        self,
        patches: list[RotatedSurfaceCode],
        x_displacer: SquareGrid.Displacer,
        z_displacer: SquareGrid.Displacer,
    ) -> list[QubitCoordinate]:
        """For a given timestep, get the circuit entries for
        a physical CX gate across all patches.

        Parameters
        ----------
        patches : List[RotatedSurfaceCode]
            The patches to consider.
        x_displacer : SquareGrid.Displacer
            The displacement for each X stabilizer.
        z_displacer : SquareGrid.Displacer
            The displacement for each Z stabilizer.

        Returns
        -------
        List[QubitCoordinate]
            A list of qubit coordinates to apply a CX gate to.
        """
        cnot_pairs: list[QubitCoordinate] = []
        for patch in patches:
            for stab in patch.x_stabilizers:
                neighbour = self.grid._get_neighbour(qubit=stab, displacer=x_displacer)
                if neighbour in patch.data_qubits:
                    cnot_pairs += [stab, neighbour]
            for stab in patch.z_stabilizers:
                neighbour = self.grid._get_neighbour(qubit=stab, displacer=z_displacer)
                if neighbour in patch.data_qubits:
                    cnot_pairs += [neighbour, stab]
        return cnot_pairs

    def _depth_4_syndrome_extraction(self, patches: list[RotatedSurfaceCode]):
        """Write a depth-4 syndrome extraction circuit to the stim circuit
        for individual patches.

        Parameters
        ----------
        patches : List[Patch]
            List of patches to perform syndrome extraction on.
        """
        x_displacer: SquareGrid.Displacer
        z_displacer: SquareGrid.Displacer
        for x_displacer, z_displacer in zip(*self.grid.schedules.values()):
            cnot_pairs = self._syndrome_extraction_circuit_entries(
                patches=patches,
                x_displacer=x_displacer,
                z_displacer=z_displacer,
            )
            self.circuit.append(TwoQubitGates.CX, targets=[q.idx for q in cnot_pairs])
            self.tick()

    def syndrome_extraction_with_detectors(self, patches: list[RotatedSurfaceCode]):
        """Perform a syndrome extraction circuit and add in detectors
        for a list of disjoint patches.

        This method is primarily for timelike invariant evolution of
        a logical qubit.

        Parameters
        ----------
        patches : List[Patch]
            List of disjoint patches to perform syndrome extraction on.
        """
        for patch in patches:
            self.reset_qubits(qubits=patch.z_stabilizers, basis=ResetGates.RZ)
            self.reset_qubits(qubits=patch.x_stabilizers, basis=ResetGates.RX)
        self.tick()

        self._depth_4_syndrome_extraction(patches=patches)

        for patch in patches:
            self.measure_qubits(qubits=patch.z_stabilizers, basis=MeasurementGates.MZ)
            self.detector_batch(patch.z_stabilizers)

            self.measure_qubits(qubits=patch.x_stabilizers, basis=MeasurementGates.MX)
            self.detector_batch(patch.x_stabilizers)
        self.timeshift()
        self.tick()

    def detector_batch(
        self,
        qubits: list[QubitCoordinate],
        new_measurements_deterministic: bool = False,
    ):
        """A convenience method for adding a batch of detectors
        during syndrome extraction rounds.

        Parameters
        ----------
        qubits : List[QubitCoordinate]
            List of qubits that have been measured.
        new_measurements_deterministic : bool, optional
            Whether or not new measurements should be deterministic, by default False.
        """
        lookback = len(qubits)
        for idx, qubit in enumerate(qubits):
            if qubit in self.measurement_record:
                self.detector(
                    qubit, [-lookback + idx, -lookback + self.measurement_record[qubit]]
                )
            else:
                if new_measurements_deterministic:
                    self.detector(qubit, [-lookback + idx])
        self._increment_measurement_record(qubits)

    def detector_batch_with_data_qubits(
        self,
        stabilizers: list[QubitCoordinate],
        data_qubit_member_check: list[QubitCoordinate],
        final_round_detector: bool = True,
    ):
        """Add a detector batch that uses some data qubit measurements.
        Use cases will be during the final round, where we want weight-5
        and weight-3 detectors, and the first round after a split
        operation where the data qubits measured in the previous round
        are needed for detectors.

        Parameters
        ----------
        stabilizers : List[QubitCoordinate]
            Stabilizers to make detectors with.
        data_qubit_member_check : List[QubitCoordinate]
            The list of data qubits we want to include in some detectors.
        final_round_detector : bool, optional
            Whether or not this is a final round detector batch, by default
            True. If True, the experiment is ended and it is assumed all
            measurements have been recorded. If False, we need to include
            the previous measurement of the stabilizer before incrementing
            the measurement record.
        """
        if final_round_detector:
            for stab in stabilizers:
                self.detector(
                    stab,
                    [
                        self.measurement_record[dq]
                        for dq in self.grid.stabilizer_data_qubit_groups(stab)
                        if dq in data_qubit_member_check
                    ]
                    + [self.measurement_record[stab]],
                )
            return
        lookback = len(stabilizers)
        for idx, stab in enumerate(stabilizers):
            self.detector(
                stab,
                [-lookback + idx, -lookback + self.measurement_record[stab]]
                + [
                    -lookback + self.measurement_record[dq]
                    for dq in self.grid.stabilizer_data_qubit_groups(stab)
                    if dq in data_qubit_member_check
                ],
            )
        self._increment_measurement_record(stabilizers)

    def grow(
        self,
        patch: RotatedSurfaceCode,
        new_distances: tuple[int, int],
        idling_patches: Optional[list[RotatedSurfaceCode]] = None,
    ) -> RotatedSurfaceCode:
        """"""
        raise NotImplementedError("Growth is a work in progress.")
        # idling_patches = idling_patches or []
        # new_dx, new_dz = new_distances
        # if new_dx <= patch.x_distance and new_dz <= patch.z_distance:
        #     raise ValueError("Calling grow function for a shrink operation.")

        # grown_patch = RotatedSurfaceCode(
        #     code_distance=new_distances,
        # qubit_grid=patch.qubit_grid, anchor=patch.anchor
        # )

        # data_qubits_to_reset: list[QubitCoordinate] = sorted(
        #     set(grown_patch.data_qubits) - set(patch.data_qubits)
        # )

        # reset_in_x_basis: list[QubitCoordinate] = list(
        #     filter(
        #         lambda data_qubit: data_qubit.x <=
        #  patch.z_distance, data_qubits_to_reset
        #     )
        # )
        # reset_in_z_basis: list[QubitCoordinate] = list(
        #     filter(
        #         lambda data_qubit: data_qubit.y <=
        #  patch.x_distance, data_qubits_to_reset
        #     )
        # ) + list(
        #     filter(
        #         lambda data_qubit: data_qubit.x > patch.z_distance
        #         and data_qubit.y > patch.x_distance,
        #         data_qubits_to_reset,
        #     )
        # )

        # self.reset_qubits(qubits=reset_in_z_basis, basis=ResetGates.RZ)
        # self.reset_qubits(qubits=reset_in_x_basis, basis=ResetGates.RX)
        # self.reset_qubits(
        #     qubits=grown_patch.z_stabilizers
        #     + [idling_patch.z_stabilizers for idling_patch in idling_patches],
        #     basis=ResetGates.RZ,
        # )
        # self.tick()

        # print(grown_patch, data_qubits_to_reset)
        # print(reset_in_x_basis)
        # print(reset_in_z_basis)
        # return

    def _draw(self, patches: list[RotatedSurfaceCode]) -> Visualiser:
        """Draw a list of patches.

        Parameters
        ----------
        patches : list[RotatedSurfaceCode]

        Returns
        -------
        Visualiser
            The visualiser object containing the figure.
        """
        vis = Visualiser(grid=self.grid)
        for patch in patches:
            for qubit in patch.data_qubits:
                vis.draw_qubit(qubit=qubit)
            for stabilizer in patch.x_stabilizers:
                vis.draw_stabilizer(
                    stabilizer=stabilizer,
                    color=Visualiser.Colors.RED,
                    data_qubit_member_check=patch.data_qubits,
                )
            for stabilizer in patch.z_stabilizers:
                vis.draw_stabilizer(
                    stabilizer=stabilizer,
                    color=Visualiser.Colors.BLUE,
                    data_qubit_member_check=patch.data_qubits,
                )

        return vis


if __name__ == "__main__":
    grid = SquareGrid(4, 4)
    a = Experiment(grid)
    a.reset_qubits(qubits=grid.data_qubits, basis=ResetGates.RZ)
