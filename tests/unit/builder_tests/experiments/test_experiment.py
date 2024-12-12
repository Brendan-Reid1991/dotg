import pytest
import stim
from builder.patches import RotatedSurfaceCode
from builder.experiments._experiment import Experiment
from builder.utilities.grids import SquareGrid
from builder.utilities import QubitCoordinate
from dotg.utilities.stim_assets import (
    StimAnnotations,
    ResetGates,
    MeasurementGates,
    OneQubitGates,
    TwoQubitGates,
)

grid = SquareGrid(4, 4)
code_a = RotatedSurfaceCode((3, 3), grid, (1, 1))


class TestExperiment:
    @pytest.fixture(scope="function")
    def experiment(self) -> Experiment:
        return Experiment(qubit_grid=grid)

    def test_circuit_initially_defined_with_qubit_coords_only(
        self, experiment: Experiment
    ):
        assert all(instr.name == "QUBIT_COORDS" for instr in experiment.circuit)

    def test_measurement_record_is_empty_and_is_dict(self, experiment: Experiment):
        assert experiment.measurement_record == {}

    def test_increment_measurement_record(self, experiment: Experiment):
        experiment._increment_measurement_record(batch=[(1, 1), (2, 2), (3, 3)])
        assert experiment.measurement_record[(1, 1)] == -3
        assert experiment.measurement_record[(2, 2)] == -2
        assert experiment.measurement_record[(3, 3)] == -1

    def test_tick(self, experiment: Experiment):
        assert experiment.circuit[-1] != stim.CircuitInstruction(
            name=StimAnnotations.TICK
        )
        experiment.tick()
        assert experiment.circuit[-1] == stim.CircuitInstruction(
            name=StimAnnotations.TICK
        )

    def test_timeshift(self, experiment: Experiment):
        assert experiment.circuit[-1].name != StimAnnotations.SHIFT_COORDS
        experiment.timeshift()
        assert experiment.circuit[-1] == stim.CircuitInstruction(
            name=StimAnnotations.SHIFT_COORDS, gate_args=[0, 0, 1]
        )

    @pytest.mark.parametrize(
        "qubits, basis",
        [
            [grid.data_qubits, ResetGates.R],
            [grid.x_stabilizers, ResetGates.RX],
            [grid.z_stabilizers, ResetGates.RZ],
            [grid.data_qubits, ResetGates.RY],
        ],
    )
    def test_reset_qubits(self, qubits, basis, experiment: Experiment):
        assert experiment.circuit[-1].name != basis
        experiment.reset_qubits(qubits=qubits, basis=basis)
        assert experiment.circuit[-1] == stim.CircuitInstruction(
            name=basis, targets=[q.idx for q in qubits]
        )

    @pytest.mark.parametrize(
        "gate",
        list(OneQubitGates.__members__.values())
        + list(TwoQubitGates.__members__.values())
        + list(MeasurementGates.__members__.values()),
    )
    def test_reset_qubits_raises_error_for_non_reset_gate(
        self, experiment: Experiment, gate
    ):
        with pytest.raises(ValueError, match="Invalid reset operation*."):
            experiment.reset_qubits(qubits=experiment.grid.data_qubits, basis=gate)

    @pytest.mark.parametrize(
        "qubits, basis",
        [
            [grid.data_qubits, MeasurementGates.M],
            [grid.x_stabilizers, MeasurementGates.MX],
            [grid.z_stabilizers, MeasurementGates.MZ],
            [grid.data_qubits, MeasurementGates.MY],
        ],
    )
    def test_measure_qubits(
        self, qubits: list[QubitCoordinate], basis, experiment: Experiment
    ):
        assert experiment.circuit[-1].name != basis
        experiment.measure_qubits(qubits=qubits, basis=basis)
        assert experiment.circuit[-1] == stim.CircuitInstruction(
            name=basis, targets=[q.idx for q in qubits]
        )

    @pytest.mark.parametrize(
        "gate",
        list(OneQubitGates.__members__.values())
        + list(TwoQubitGates.__members__.values())
        + list(ResetGates.__members__.values()),
    )
    def test_measure_qubits_raises_error_for_non_measure_gate(
        self, experiment: Experiment, gate
    ):
        with pytest.raises(ValueError, match="Invalid measurement operation*."):
            experiment.measure_qubits(qubits=experiment.grid.data_qubits, basis=gate)

    @pytest.mark.parametrize(
        "gate, qubits",
        [
            [OneQubitGates.X, grid.data_qubits],
            [OneQubitGates.SQRT_X, grid.data_qubits],
            [OneQubitGates.Y, grid.data_qubits],
            [OneQubitGates.SQRT_X_DAG, grid.data_qubits],
            [
                TwoQubitGates.CZ,
                [
                    grid.data_qubits[0],
                    grid.z_stabilizers[0],
                    grid.data_qubits[-1],
                    grid.x_stabilizers[-1],
                ],
            ],
            [
                TwoQubitGates.CX,
                [
                    grid.data_qubits[0],
                    grid.z_stabilizers[0],
                    grid.data_qubits[-1],
                    grid.x_stabilizers[-1],
                ],
            ],
        ],
    )
    def test_apply_gate(
        self,
        qubits: list[QubitCoordinate],
        gate: OneQubitGates | TwoQubitGates,
        experiment: Experiment,
    ):
        assert experiment.circuit[-1].name != gate
        experiment.apply_gate(qubits=qubits, gate=gate)
        assert experiment.circuit[-1] == stim.CircuitInstruction(
            name=gate, targets=[q.idx for q in qubits]
        )

    @pytest.mark.parametrize(
        "gate",
        list(MeasurementGates.__members__.values())
        + list(ResetGates.__members__.values()),
    )
    def test_apply_gate_raises_error_for_non_quantum_op_gate(
        self, experiment: Experiment, gate
    ):
        with pytest.raises(ValueError, match="Invalid gate operation*."):
            experiment.apply_gate(qubits=experiment.grid.data_qubits, gate=gate)

    @pytest.mark.parametrize(
        "callable, invalid_qubits, _gate",
        [
            ["reset_qubits", [0, 1, 2, 3, 4], "R"],
            ["measure_qubits", ["s", 10.01], "M"],
            ["apply_gate", [0.01, QubitCoordinate(1, 0)], "CX"],
        ],
    )
    def test_non_qubit_coordinate_objects_raise_valueerror(
        self, callable, invalid_qubits, _gate, experiment
    ):
        with pytest.raises(
            ValueError,
            match="Some qubits are not QubitCoordinate objects",
        ):
            getattr(experiment, callable)(invalid_qubits, _gate)

    @pytest.mark.parametrize(
        "callable, invalid_qubits, _gate",
        [
            ["reset_qubits", [QubitCoordinate(0, 2)], "R"],
            ["measure_qubits", [QubitCoordinate(0, 2)], "M"],
            ["apply_gate", [QubitCoordinate(0, 2)], "X"],
        ],
    )
    def test_qubitcoords_without_indices_raises_error(
        self, callable, invalid_qubits, _gate, experiment
    ):
        with pytest.raises(
            ValueError,
            match="QubitCoordinate index is not defined!",
        ):
            getattr(experiment, callable)(invalid_qubits, _gate)

    @pytest.mark.parametrize(
        "callable, _gate",
        [
            ["reset_qubits", "R"],
            ["measure_qubits", "M"],
            ["apply_gate", "X"],
        ],
    )
    def test_repeated_qubits_raises_error(self, callable, _gate, experiment: Experiment):
        qubits = experiment.grid.data_qubits * 2
        with pytest.raises(
            ValueError,
            match="Some qubits have the same indices.",
        ):
            getattr(experiment, callable)(qubits, _gate)

    @pytest.mark.parametrize(
        "qubit, targets",
        [
            [QubitCoordinate(0, 2), [-1, -2]],
            [QubitCoordinate(1, 3), [-1, -2, -3]],
            [QubitCoordinate(300, 400), -45],
        ],
    )
    def test_detector(self, experiment: Experiment, qubit, targets):
        assert experiment.circuit[-1].name != StimAnnotations.DETECTOR
        experiment.detector(qubit=qubit, targets=targets)
        instr: stim.CircuitInstruction = experiment.circuit[-1]

        assert instr.name == StimAnnotations.DETECTOR
        assert instr.gate_args_copy() == list(qubit) + [0]
        assert instr.targets_copy() == list(
            map(stim.target_rec, [targets] if isinstance(targets, int) else targets)
        )

    def test_observable(self, experiment: Experiment):
        assert experiment.circuit[-1].name != StimAnnotations.OBSERVABLE_INCLUDE
        index = 0
        targets = [-1, -2, -3, -4]
        experiment.observable(index, targets)
        instr: stim.CircuitInstruction = experiment.circuit[-1]

        assert instr.name == StimAnnotations.OBSERVABLE_INCLUDE
        assert instr.gate_args_copy() == [0]
        assert instr.targets_copy() == list(map(stim.target_rec, targets))

    def test_syndrome_extraction_circuit_entries(self, experiment: Experiment):
        assert experiment._syndrome_extraction_circuit_entries(
            patches=[code_a],
            x_displacer=grid.schedules["x"][0],
            z_displacer=grid.schedules["z"][0],
        ) == [
            (1.5, 0.5),
            (1, 1),
            (1.5, 2.5),
            (1, 3),
            (2.5, 1.5),
            (2, 2),
            (1, 2),
            (1.5, 1.5),
            (2, 3),
            (2.5, 2.5),
            (3, 2),
            (3.5, 1.5),
        ]

    def test_depth_4_syndrome_extraction(self, experiment: Experiment):
        assert "CX" not in [instr.name for instr in experiment.circuit]
        experiment._depth_4_syndrome_extraction(patches=[code_a])
        assert experiment.circuit[-8:] == stim.Circuit(
            """CX 10 0 11 2 12 4 1 16 5 19 7 20
            TICK
            CX 10 3 11 5 12 7 0 16 4 19 6 20
            TICK
            CX 11 1 12 3 13 5 2 15 4 16 8 19
            TICK
            CX 11 4 12 6 13 8 1 15 3 16 7 19
            TICK"""
        )

    def test_syndrome_extraction_with_detectors(self, experiment: Experiment):
        experiment.initialize_patches(patches=[code_a], logical_bases=["X"])
        assert experiment.circuit[-7:-3] == stim.Circuit(
            """DETECTOR(1.5, 0.5, 0) rec[-4]
            DETECTOR(1.5, 2.5, 0) rec[-3]
            DETECTOR(2.5, 1.5, 0) rec[-2]
            DETECTOR(2.5, 3.5, 0) rec[-1]"""
        )
        experiment.syndrome_extraction_with_detectors(patches=[code_a])
        assert experiment.circuit[-23:] == stim.Circuit(
            """R 15 16 19 20
            RX 10 11 12 13
            TICK
            CX 10 0 11 2 12 4 1 16 5 19 7 20
            TICK
            CX 10 3 11 5 12 7 0 16 4 19 6 20
            TICK
            CX 11 1 12 3 13 5 2 15 4 16 8 19
            TICK
            CX 11 4 12 6 13 8 1 15 3 16 7 19
            TICK
            M 15 16 19 20
            DETECTOR(0.5, 2.5, 0) rec[-4] rec[-8]
            DETECTOR(1.5, 1.5, 0) rec[-3] rec[-7]
            DETECTOR(2.5, 2.5, 0) rec[-2] rec[-6]
            DETECTOR(3.5, 1.5, 0) rec[-1] rec[-5]
            MX 10 11 12 13
            DETECTOR(1.5, 0.5, 0) rec[-4] rec[-16]
            DETECTOR(1.5, 2.5, 0) rec[-3] rec[-15]
            DETECTOR(2.5, 1.5, 0) rec[-2] rec[-14]
            DETECTOR(2.5, 3.5, 0) rec[-1] rec[-13]
            SHIFT_COORDS(0, 0, 1)
            TICK"""
        )


if __name__ == "__main__":
    exp = Experiment(grid)
    exp.initialize_patches(patches=[code_a], logical_bases=["X"])
    exp.syndrome_extraction_with_detectors(patches=[code_a])
    print(exp.circuit)
