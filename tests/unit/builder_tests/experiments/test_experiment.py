import pytest
import stim
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

grid = SquareGrid(3, 3)


class TestExperiment:
    @pytest.fixture(scope="class")
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
