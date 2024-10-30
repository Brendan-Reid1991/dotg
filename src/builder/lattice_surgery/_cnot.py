from typing import List, Dict, Optional, Tuple, Iterable, Literal
from enum import Enum, auto
import stim

from builder.utilities import Visualiser, QubitCoordinate
from builder.utilities.grids import SquareGrid
from builder.patches import RotatedSurfaceCode
from builder.lattice_surgery._experiment import LatticeSurgeryExperiment


from dotg.utilities.stim_assets import (
    ResetGates,
    MeasurementGates,
    TwoQubitGates,
    OneQubitGates,
)

Basis = Literal["X", "Z"]


class CXExperiment(LatticeSurgeryExperiment):
    """A class that controls a logical CX experiment in lattice surgery.

    This experiment has three logical qubit patches: the control patch,
    the target patch, and the ancilla patch.

    The experiment itself is separated into Stages, called "DISJOINT",
    "CONTROL_ANCILLA" and "TARGET_ANCILLA".

    As the logical CX involves first preparing three separate logical
    qubits ("DISJOINT") followed by an XX merge between the control
    and the ancilla patch ("CONTROL_ANCILLA"). There is then a split
    operation (back to "DISJOINT") before a ZZ merge between target
    and ancilla ("TARGET_ANCILLA"). Finally, a split between these
    two patches (back to "DISJOINT").

    At present we only support preparing the control state in |+>
    and the target state in |0>.

    The observables for other cases have not been mapped out.

    Parameters
    ----------
    code_distance: int
        The X/Z code distance for each logical patch.
    control_state: Basis
        The state of the control qubit, by default "Z" which
        in this case prepares a logical |1> state.
    target_state: Basis
        The state of the target qubit, by default "Z" which
        in this case prepares a logical |0> state.
    control_target_joint_measurement_basis: MeasurementGates | str, optional
        Measurement basis for control and target qubits for
        control_state="X" and target_state="Z", as this
        experiment has two valid outcomes.
    intermediate_rows_or_columns: int, optional
        How many rows or columns of data qubits to place between
        logical patches, by default 1.
    """

    class Stage(Enum):
        """An enum to designate the stages of a CX experiment.

        The three distinct stages are
        - DISJOINT
        - CONTROL_ANCILLA
        - TARGET_ANCILLA
        - CONTROL_TARGET_ONLY
        """

        DISJOINT = auto()
        CONTROL_ANCILLA = auto()
        TARGET_ANCILLA = auto()
        CONTROL_TARGET_ONLY = auto()

    def __init__(
        self,
        code_distance: int,
        control_state: Basis = "Z",
        target_state: Basis = "Z",
        control_target_joint_measurement_basis: Optional[MeasurementGates | str] = None,
        intermediate_rows_or_columns: int = 1,
    ) -> None:

        self.code_distance = code_distance
        self.intermediate_rows_or_columns = intermediate_rows_or_columns

        self.control_state = control_state
        self.target_state = target_state

        if (self.control_state, self.target_state) not in [
            ("X", "Z"),
            ("Z", "Z"),
        ]:
            raise ValueError(
                f"""Invalid state preparations for (control, target) logical qubits: ({self.control_state}, {self.target_state}). 
                             Must be either ("Z", "Z") to run CX(|1>, |0>) or 
                             ("X", "Z") to run CX(|+>, |0>)."""
            )

        self.control_target_joint_measurement_basis = (
            control_target_joint_measurement_basis
        )
        if (self.control_state, self.target_state) == (
            "X",
            "Z",
        ) and not self.control_target_joint_measurement_basis:
            raise ValueError(
                """Experiment will prepare a Bell state between control and target qubits, but a joint measurement basis has not been specified. Set it with `control_target_joint_measurement_basis` kwarg."""
            )

        super().__init__(
            SquareGrid(
                2 * self.code_distance + self.intermediate_rows_or_columns + 1,
                2 * self.code_distance + self.intermediate_rows_or_columns + 1,
            )
        )

        self.control_patch = RotatedSurfaceCode(
            code_distance=(
                self.code_distance,
                self.code_distance,
            ),
            qubit_grid=self.grid,
            anchor=(1, 1),
        )

        self.target_patch = RotatedSurfaceCode(
            code_distance=(
                self.code_distance,
                self.code_distance,
            ),
            qubit_grid=self.grid,
            anchor=(
                self.code_distance + self.intermediate_rows_or_columns + 1,
                self.code_distance + self.intermediate_rows_or_columns + 1,
            ),
        )

        self.ancilla_patch = RotatedSurfaceCode(
            code_distance=(
                self.code_distance,
                self.code_distance,
            ),
            qubit_grid=self.grid,
            anchor=(
                1,
                self.code_distance + self.intermediate_rows_or_columns + 1,
            ),
        )

        self.control_ancilla_patch = RotatedSurfaceCode(
            code_distance=(
                2 * self.code_distance + self.intermediate_rows_or_columns,
                self.code_distance,
            ),
            qubit_grid=self.grid,
            anchor=(1, 1),
        )

        self.target_ancilla_patch = RotatedSurfaceCode(
            code_distance=(
                self.code_distance,
                2 * self.code_distance + self.intermediate_rows_or_columns,
            ),
            qubit_grid=self.grid,
            anchor=(
                1,
                self.code_distance + self.intermediate_rows_or_columns + 1,
            ),
        )

        self.control_ancilla_inactive_data: List[QubitCoordinate] = [
            dq
            for dq in self.grid.data_qubits
            if self.code_distance
            < dq.y
            < self.code_distance + self.intermediate_rows_or_columns + 1
            and 1 <= dq.x <= self.code_distance
        ]

        self.control_ancilla_inactive_z_stabilizers: List[QubitCoordinate] = [
            stab
            for stab in self.grid.z_stabilizers
            if 0 < stab.x < self.code_distance + 1
            and self.code_distance
            < stab.y
            < self.code_distance + intermediate_rows_or_columns + 1
        ]

        # We expect this to be empty for intermediate_rows_or_columns=1
        self.control_ancilla_inactive_x_stabilizers: List[QubitCoordinate] = [
            stab
            for stab in self.grid.x_stabilizers
            if 1 < stab.x < self.code_distance
            and self.code_distance
            < stab.y
            <= self.code_distance + self.intermediate_rows_or_columns
            and stab
            not in self.ancilla_patch.x_stabilizers + self.control_patch.x_stabilizers
        ]

        self.target_ancilla_inactive_data: List[QubitCoordinate] = [
            dq
            for dq in self.grid.data_qubits
            if self.code_distance
            < dq.x
            < self.code_distance + self.intermediate_rows_or_columns + 1
            and self.code_distance + self.intermediate_rows_or_columns + 1
            <= dq.y
            <= 2 * self.code_distance + self.intermediate_rows_or_columns
        ]

        self.target_ancilla_inactive_x_stabilizers: List[QubitCoordinate] = [
            stab
            for stab in self.grid.x_stabilizers
            if self.code_distance
            < stab.x
            < self.code_distance + intermediate_rows_or_columns + 1
            and self.code_distance + self.intermediate_rows_or_columns
            < stab.y
            < 2 * self.code_distance + self.intermediate_rows_or_columns + 1
        ]

        # Similarly, should be empty for intermediate_rows_or_columns=1
        self.target_ancilla_inactive_z_stabilizers: List[QubitCoordinate] = [
            stab
            for stab in self.grid.z_stabilizers
            if self.code_distance
            < stab.x
            <= self.code_distance + intermediate_rows_or_columns + 1
            and self.code_distance + self.intermediate_rows_or_columns + 1
            < stab.y
            < 2 * self.code_distance + self.intermediate_rows_or_columns
            and stab
            not in self.ancilla_patch.z_stabilizers + self.target_patch.z_stabilizers
        ]

        self.logical_qubit_states: Dict[RotatedSurfaceCode, Basis] = {
            self.control_patch: self.control_state,
            self.ancilla_patch: "X",
            self.target_patch: self.target_state,
        }

    def _active_patches(self, stage: Stage) -> List[RotatedSurfaceCode]:
        """Get a list of active patches given the stage of the
        experiment.

        Parameters
        ----------
        stage : Stage
            The current experiment Stage.

        Returns
        -------
        List[RotatedSurfaceCode]
            A list of active patches.

        Raises
        ------
        ValueError
            If an invalid Stage is provided.
        """
        if stage is CXExperiment.Stage.DISJOINT:
            return [self.control_patch, self.target_patch, self.ancilla_patch]
        elif stage is CXExperiment.Stage.CONTROL_ANCILLA:
            return [self.control_ancilla_patch, self.target_patch]
        elif stage is CXExperiment.Stage.TARGET_ANCILLA:
            return [self.control_patch, self.target_ancilla_patch]
        elif stage is CXExperiment.Stage.CONTROL_TARGET_ONLY:
            return [self.control_patch, self.target_patch]
        else:
            raise ValueError(
                "No appropriate stage chosen for syndrome extraction. It has to be one of them."
            )

    def get_logicals(self) -> Iterable[List[QubitCoordinate]]:
        """Based on the input logical states and specified measurement basis,
        get a list of logical operators.

        Returns
        -------
        Iterable[List[QubitCoordinate]]
            A list of logical operators.
        """
        if (self.control_state, self.target_state) == ("Z", "Z"):
            return [
                self.control_patch.bottom_boundary_data,
                self.target_patch.bottom_boundary_data
                + [
                    q
                    for q in self.target_ancilla_inactive_data
                    if q.y == self.target_patch.bottom_boundary_data[0].y
                ],
            ]
        if (self.control_state, self.target_state) == (
            "X",
            "Z",
        ) and self.control_target_joint_measurement_basis == MeasurementGates.MX:
            return [
                self.target_patch.left_boundary_data
                + self.control_patch.right_boundary_data
                + [
                    q
                    for q in self.control_ancilla_inactive_data
                    if q.x == self.control_patch.right_boundary_data[0].x
                ]
            ]
        if (self.control_state, self.target_state) == (
            "X",
            "Z",
        ) and self.control_target_joint_measurement_basis == MeasurementGates.MZ:
            return [
                self.target_patch.bottom_boundary_data
                + [
                    q
                    for q in self.target_ancilla_inactive_data
                    if q.y == self.target_patch.bottom_boundary_data[0].y
                ]
                + self.control_patch.top_boundary_data
            ]

        raise ValueError("Couldn't find logical operators!")

    def reset_data(self):
        """Reset the data qubits in each disjoint patch."""
        for patch, logical_state in self.logical_qubit_states.items():
            self.reset_qubits(
                patch.data_qubits,
                ResetGates.RZ if logical_state == "Z" else ResetGates.RX,
            )

    def initialize_patches(self):
        """Initialize the individual patches in their respective logical states."""
        patches = self._active_patches(stage=CXExperiment.Stage.DISJOINT)
        self.reset_data()
        self.reset_stabilizers(patches=patches)
        self.tick()
        if self.control_state == "Z":
            self.apply_gate(self.control_patch.data_qubits, OneQubitGates.X)
            self.tick()
        self._depth_4_syndrome_extraction(patches=patches)

        for patch in patches:
            logical = self.logical_qubit_states[patch]

            self.measure_qubits(patch.z_stabilizers, MeasurementGates.MZ)
            self.detector_batch(patch.z_stabilizers, logical == "Z")

            self.measure_qubits(patch.x_stabilizers, MeasurementGates.MX)
            self.detector_batch(patch.x_stabilizers, logical == "X")
        self.timeshift()
        self.tick()

    def _reset_control_ancilla_data(self):
        """Reset the data qubits for the control-ancilla merge step."""
        self.reset_qubits(self.control_ancilla_inactive_data, ResetGates.RX)

    def _reset_target_ancilla_data(self):
        """Reset the data qubits for the target-ancilla merge step."""
        self.reset_qubits(self.target_ancilla_inactive_data, ResetGates.RZ)

    def reset_stabilizers(self, patches: List[RotatedSurfaceCode]):
        for patch in patches:
            self.reset_qubits(patch.z_stabilizers, ResetGates.RZ)
            self.reset_qubits(patch.x_stabilizers, ResetGates.RX)

    def syndrome_extraction(self, rounds: int, stage: Stage):
        """Do multiple rounds of syndrome extraction and adding detectors
        for a specific Stage of the experiment.

        Parameters
        ----------
        rounds : int
            How many rounds of syndrome extraction to perform.
        stage : Stage
            Which Stage of the experiment we are in.
        """
        patches = self._active_patches(stage=stage)

        for _ in range(rounds):
            self.reset_stabilizers(patches=patches)
            self.tick()
            self._depth_4_syndrome_extraction(patches=patches)
            for patch in patches:
                self.measure_qubits(patch.z_stabilizers, MeasurementGates.MZ)
                self.detector_batch(patch.z_stabilizers)

                self.measure_qubits(patch.x_stabilizers, MeasurementGates.MX)
                self.detector_batch(patch.x_stabilizers)

            self.timeshift()
            self.tick()

    def end_experiment(self):
        """End the experiment."""

        self.measure_ancilla()
        self.classically_controlled_gates()
        self.syndrome_extraction(
            self.code_distance, stage=CXExperiment.Stage.CONTROL_TARGET_ONLY
        )
        self.measure_control_and_target_qubits(
            basis=self.control_target_joint_measurement_basis or MeasurementGates.MZ
        )
        for idx, logical_targets in enumerate(self.get_logicals()):
            self.observable(idx, [self.measurement_record[q] for q in logical_targets])

    def control_ancilla_merge(self):
        """Merge the control and ancilla patches. This method also performs
        the first round of syndrome extraction after the merge and adds
        deterministic detectors.
        """
        patches = self._active_patches(stage=CXExperiment.Stage.CONTROL_ANCILLA)
        self.reset_qubits(self.control_ancilla_inactive_data, ResetGates.RX)
        self.reset_stabilizers(patches=patches)
        self.tick()
        self._depth_4_syndrome_extraction(patches=patches)

        for patch in patches:
            self.measure_qubits(patch.z_stabilizers, MeasurementGates.MZ)
            self.detector_batch(patch.z_stabilizers)

            self.measure_qubits(patch.x_stabilizers, MeasurementGates.MX)
            self.detector_batch(patch.x_stabilizers, True)
        self.timeshift()
        self.tick()

    def control_ancilla_split(self):
        """Split the control and ancilla patches.

        The first round of syndrome extraction after the split requires some
        bespoke detectors, and so this method also introduces that round into
        the circuit.
        """

        # Measure out the intermediate data qubits
        self.measure_qubits(self.control_ancilla_inactive_data, MeasurementGates.MX)
        self._increment_measurement_record(self.control_ancilla_inactive_data)

        # If self.intermediate_rows_or_columns > 1
        # we must add higher weight detectors to create
        # a timelike boundary in the decoding graph.
        self.detector_batch_with_data_qubits(
            stabilizers=self.control_ancilla_inactive_x_stabilizers,
            data_qubit_member_check=self.control_ancilla_inactive_data,
            final_round_detector=True,
        )

        # Perform syndrome extraction now on the disjoint patches.
        patches = self._active_patches(stage=CXExperiment.Stage.DISJOINT)
        self.reset_stabilizers(patches=patches)
        self.tick()
        self._depth_4_syndrome_extraction(patches=patches)
        for patch in patches:
            # Add the detectors for Z and X stabilizers
            self.measure_qubits(patch.z_stabilizers, MeasurementGates.MZ)
            self.detector_batch(patch.z_stabilizers)

            self.measure_qubits(patch.x_stabilizers, MeasurementGates.MX)
            self.detector_batch_with_data_qubits(
                stabilizers=patch.x_stabilizers,
                data_qubit_member_check=self.control_ancilla_inactive_data,
                final_round_detector=False,
            )
        self.timeshift()
        self.tick()

    def target_ancilla_merge(self):
        """Merge the target and ancilla patches along their Z boundaries."""
        patches = self._active_patches(stage=CXExperiment.Stage.TARGET_ANCILLA)
        self.reset_qubits(self.target_ancilla_inactive_data, ResetGates.RZ)
        self.reset_stabilizers(patches)
        self.tick()
        self._depth_4_syndrome_extraction(patches)

        for patch in patches:
            self.measure_qubits(patch.z_stabilizers, MeasurementGates.MZ)
            self.detector_batch(patch.z_stabilizers, True)
            self.measure_qubits(patch.x_stabilizers, MeasurementGates.MX)
            self.detector_batch(patch.x_stabilizers)
        self.timeshift()
        self.tick()

    def target_ancilla_split(self):
        """Split the target and ancilla patches. This also adds
        one round of syndrome extraction.
        """
        self.measure_qubits(self.target_ancilla_inactive_data, MeasurementGates.MZ)
        self._increment_measurement_record(self.target_ancilla_inactive_data)
        self.detector_batch_with_data_qubits(
            stabilizers=self.target_ancilla_inactive_z_stabilizers,
            data_qubit_member_check=self.target_ancilla_inactive_data,
            final_round_detector=True,
        )

        patches = self._active_patches(stage=CXExperiment.Stage.DISJOINT)
        self.reset_stabilizers(patches)
        self.tick()
        self._depth_4_syndrome_extraction(patches)
        for patch in patches:
            self.measure_qubits(patch.z_stabilizers, MeasurementGates.MZ)
            self.detector_batch_with_data_qubits(
                stabilizers=patch.z_stabilizers,
                data_qubit_member_check=self.target_ancilla_inactive_data,
                final_round_detector=False,
            )
            self.measure_qubits(patch.x_stabilizers, MeasurementGates.MX)
            self.detector_batch(patch.x_stabilizers)
        self.timeshift()
        self.tick()

    def measure_ancilla(self):
        """Measure the ancilla patch in the Z basis."""
        self.measure_qubits(self.ancilla_patch.data_qubits, MeasurementGates.MZ)
        self._increment_measurement_record(self.ancilla_patch.data_qubits)
        self.detector_batch_with_data_qubits(
            stabilizers=self.ancilla_patch.z_stabilizers,
            data_qubit_member_check=self.ancilla_patch.data_qubits,
            final_round_detector=True,
        )

    def measure_control_and_target_qubits(self, basis: MeasurementGates):
        """Measure out the control and target qubits in the specified basis.

        Parameters
        ----------
        basis : MeasurementGates
            Which basis to measure the patches in.
        """
        for patch, gate in zip([self.control_patch, self.target_patch], [basis] * 2):
            self.measure_qubits(patch.data_qubits, gate)
            self._increment_measurement_record(patch.data_qubits)
            self.detector_batch_with_data_qubits(
                stabilizers=(
                    patch.z_stabilizers
                    if basis == MeasurementGates.MZ
                    else patch.x_stabilizers
                ),
                data_qubit_member_check=patch.data_qubits,
                final_round_detector=True,
            )

    def classically_controlled_gates(self):
        """Apply a Z logical onto the control patch, conditioned on the outcome
        of the XX measurement between the target and ancilla patches.

        Apply an X logical onto the target patch, conditioned on the outcome of
        the ZZ measurement between the control and ancilla patches, and the
        logical Z value of the ancilla patch (read: the Z value of the control
        patch).
        """
        control_patch_condition = self.target_ancilla_inactive_x_stabilizers
        target_patch_condition = (
            self.control_ancilla_inactive_z_stabilizers
            + self.ancilla_patch.bottom_boundary_data
        )
        for qubit in self.control_patch.bottom_boundary_data:
            for meas in control_patch_condition:
                self.circuit.append(
                    TwoQubitGates.CZ,
                    [stim.target_rec(self.measurement_record[meas]), qubit.idx],
                )
        for qubit in self.target_patch.left_boundary_data:
            for meas in target_patch_condition:
                self.circuit.append(
                    TwoQubitGates.CX,
                    [stim.target_rec(self.measurement_record[meas]), qubit.idx],
                )
        self.tick()

    def draw(
        self,
        show: Stage | str,
        figsize: Tuple[int, int] = (15, 12),
        highlight_logicals: bool = False,
        highlight_nondeterminisms: bool = False,
    ) -> Visualiser:
        """Draw function using the new visualiser class.

        Parameters
        ----------
        show : Stage | str
            Which Stage of the experiment to show.
            Arguments are:
                - CXExperiment.Stage.DISJOINT
                - CXExperiment.Stage.CONTROL_ANCILLA
                - CXExperiment.Stage.TARGET_ANCILLA
                - "All".
            Where all shows the individual patches and intermediate
            stabilizers and data qubits grayed out.
        figsize : Tuple[int, int], optional
            Matplotlib figure size, by default (15, 12)
        highlight_logicals : bool, optional
            Whether or not to highlight the logicals
            in this experiment, by default False.
        highlight_nondeterminisms : bool, optional
            Whether or not to highlight any nondeterminisms
            arising in the detector error model, by default False.

        Returns
        -------
        Visualiser
            A visualiser object.

        Raises
        ------
        ValueError
            If an invalid 'show' keyword is provided.
        """
        if isinstance(show, CXExperiment.Stage):
            patches = self._active_patches(stage=show)
            show_all = None
        elif show.lower() != "all":
            raise ValueError(
                "Invalid value for 'show' keyword. Must be one of the Stages from CXExperiment.Stage or 'All'."
            )
        else:
            patches = self._active_patches(stage=CXExperiment.Stage.DISJOINT)
            show_all = True

        vis = Visualiser(grid=self.grid, figsize=figsize, show_indices=True)

        for patch in patches:
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
            for qubit in patch.data_qubits:
                vis.draw_qubit(qubit)

        if show_all:
            for stabilizer in self.control_ancilla_inactive_x_stabilizers:
                vis.draw_stabilizer(
                    stabilizer,
                    "red",
                    data_qubit_member_check=self.control_ancilla_patch.data_qubits,
                    opacity=0.2,
                    fade_index=True,
                )
            for stabilizer in self.control_ancilla_inactive_z_stabilizers:
                vis.draw_stabilizer(
                    stabilizer,
                    "blue",
                    data_qubit_member_check=self.control_ancilla_patch.data_qubits,
                    opacity=0.2,
                    fade_index=True,
                )
            for stabilizer in self.target_ancilla_inactive_x_stabilizers:
                vis.draw_stabilizer(
                    stabilizer,
                    "red",
                    data_qubit_member_check=self.target_ancilla_patch.data_qubits,
                    opacity=0.2,
                    fade_index=True,
                )
            for stabilizer in self.target_ancilla_inactive_z_stabilizers:
                vis.draw_stabilizer(
                    stabilizer,
                    "blue",
                    data_qubit_member_check=self.target_ancilla_patch.data_qubits,
                    opacity=0.2,
                    fade_index=True,
                )
            for qubit in (
                self.control_ancilla_inactive_data + self.target_ancilla_inactive_data
            ):
                vis.draw_qubit(qubit, patch_opacity=0.4, text_opacity=0.5)

        return vis

    def run_experiment(self, num_rounds_between_each_stage: Optional[int] = None):
        """_summary_

        Parameters
        ----------
        num_rounds_between_each_stage : Optional[int], optional
            _description_, by default None
        """
        num_rounds_between_each_stage = (
            num_rounds_between_each_stage or self.code_distance - 1
        )
        self.initialize_patches()
        self.syndrome_extraction(
            stage=CXExperiment.Stage.DISJOINT, rounds=num_rounds_between_each_stage - 1
        )

        self.control_ancilla_merge()
        self.syndrome_extraction(
            stage=CXExperiment.Stage.CONTROL_ANCILLA,
            rounds=num_rounds_between_each_stage - 1,
        )

        self.control_ancilla_split()
        self.syndrome_extraction(
            stage=CXExperiment.Stage.DISJOINT,
            rounds=1,
        )

        self.target_ancilla_merge()
        self.syndrome_extraction(
            stage=CXExperiment.Stage.TARGET_ANCILLA,
            rounds=num_rounds_between_each_stage - 1,
        )

        self.target_ancilla_split()

        self.end_experiment()
