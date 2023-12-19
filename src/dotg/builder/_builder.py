from __future__ import annotations
from typing import List
import stim
from dotg.utilities.stim_assets import (
    TwoQubitGates,
    OneQubitGates,
    ResetGates,
    MeasurementGates,
    StimGate,
    StimDecorators,
)


class Qubit:
    def __init__(self, *args) -> None:
        self.identifiers = tuple(args)

        self._iterator = (id for id in self.identifiers)

    def __add__(self, other: Qubit):
        if not len(self.identifiers) == len(other.identifiers):
            raise ValueError("Can't add these two!")
        if len(self.identifiers) == 1:
            return Qubit(self.identifiers[0] + other.identifiers[0])
        return Qubit(*[x + y for x, y in zip(self.identifiers, other.identifiers)])

    def __repr__(self) -> str:
        _str = "Qubit(" + ", ".join(map(str, self.identifiers)) + ")"
        return _str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Qubit):
            return False
        return self.identifiers == other.identifiers

    def __hash__(self) -> int:
        return sum(hash(x) for x in self.identifiers)

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        return next(self._iterator)


class RotatedPlanarCircuitBuilder:
    def __init__(self, distance: int, rounds: int, logical_memory: str = "Z"):
        self.distance = distance
        self.rounds = rounds
        self.logical_memory = logical_memory

        x_dim = 2 * self.distance + 1
        y_dim = 2 * self.distance + 1

        self.data_qubits = [
            Qubit(x, y) for x in range(1, x_dim, 2) for y in range(1, y_dim, 2)
        ]
        self.x_auxiliary_qubits = []
        # X stabilisers
        offset = 0
        for x in range(2, (x_dim - 1), 2):
            ylow = 0 + 2 * (offset % 2)
            yhigh = y_dim + (1 - self.distance % 2)
            for y in range(ylow, yhigh, 4):
                self.x_auxiliary_qubits.append(Qubit(x, y))
            offset += 1

        # Z stabilisers
        self.z_auxiliary_qubits = []
        offset = 1
        for y in range(2, y_dim - 1, 2):
            xlow = 0 + 2 * (offset % 2)
            xhigh = x_dim
            for x in range(xlow, xhigh, 4):
                self.z_auxiliary_qubits.append(Qubit(x, y))
            offset += 1

        self.aux_qubits = self.x_auxiliary_qubits + self.z_auxiliary_qubits

        # coordinates are sorted by the y-coordinate,
        # then x-coordinate, for consistent indexing
        self.qubits = sorted(
            self.data_qubits + self.aux_qubits,
            key=lambda q: q.identifiers[::-1],
        )

        # append the qubits to the stim circuit
        self.circuit = stim.Circuit()
        self._qubit_mapping = {}
        for idx, qubit in enumerate(self.qubits):
            self.circuit.append("QUBIT_COORDS", idx, qubit.identifiers)
            self._qubit_mapping[qubit] = idx

        self.layer(ResetGates.RZ, self.qubits)

    def apply(self, gate: StimGate, qubits: List[Qubit] | Qubit) -> None:
        qubits = [qubits] if not isinstance(qubits, list) else qubits
        if any(isinstance(x, Qubit) for x in qubits):
            if not all(isinstance(x, Qubit) for x in qubits):
                raise ValueError("Mismatch of integer and Qubit objects for qubit ids")
            qubits = list(map(self.map_qubit, qubits))
        self.circuit.append(name=gate, targets=qubits)

    def time_step(self):
        self.circuit.append(name="TICK")

    def layer(self, gate: StimGate, qubits: List[Qubit]) -> None:
        self.apply(gate=gate, qubits=qubits)
        self.time_step()

    def map_qubit(self, qubit: Qubit) -> int:
        return self._qubit_mapping[qubit]

    def measure_all_z_syndromes(self):
        nearby_sites = [Qubit(-1, 1), Qubit(-1, -1), Qubit(1, 1), Qubit(1, -1)]

        for site in nearby_sites:
            qubits_in_this_step = []
            for qubit in self.z_auxiliary_qubits:
                if qubit + site in self.data_qubits:
                    qubits_in_this_step += [qubit + site, qubit]

            self.layer(gate=TwoQubitGates.CX, qubits=qubits_in_this_step)

    def measure_all_x_syndromes(self):
        nearby_sites = [Qubit(-1, 1), Qubit(1, 1), Qubit(-1, -1), Qubit(1, -1)]
        self.layer(gate=OneQubitGates.H, qubits=self.x_auxiliary_qubits)

        for site in nearby_sites:
            qubits_in_this_step = []
            for qubit in self.x_auxiliary_qubits:
                if qubit + site in self.data_qubits:
                    qubits_in_this_step += [qubit, qubit + site]
            self.layer(gate=TwoQubitGates.CNOT, qubits=qubits_in_this_step)
        self.layer(gate=OneQubitGates.H, qubits=self.x_auxiliary_qubits)

    def measure_auxiliaries(self):
        self.layer(MeasurementGates.MZ, self.aux_qubits)

    def syndrome_extraction_round(self, interlaced: bool = False):
        if interlaced:
            self.perform_interlaced_schedule()
        else:
            self.measure_all_x_syndromes()
            self.measure_all_z_syndromes()
        self.measure_auxiliaries()

    def perform_interlaced_schedule(self):
        z_schedule = [Qubit(-1, 1), Qubit(-1, -1), Qubit(1, 1), Qubit(1, -1)]
        x_schedule = [Qubit(-1, 1), Qubit(1, 1), Qubit(-1, -1), Qubit(1, -1)]

        self.layer(OneQubitGates.H, self.x_auxiliary_qubits)

        for x_site, z_site in zip(x_schedule, z_schedule):
            qubits_in_this_step = []
            for x_aux in self.x_auxiliary_qubits:
                if x_aux + x_site in self.data_qubits:
                    qubits_in_this_step += [x_aux, x_aux + x_site]
            for z_aux in self.z_auxiliary_qubits:
                if z_aux + z_site in self.data_qubits:
                    qubits_in_this_step += [z_aux + z_site, z_aux]
            self.layer(TwoQubitGates.CNOT, qubits_in_this_step)
        self.layer(OneQubitGates.H, self.x_auxiliary_qubits)

    def nth_round_detector(self, qubit: Qubit, round: int):
        measurement_lookback = -len(self.aux_qubits) + self.aux_qubits.index(qubit)
        previous_round_lookback = measurement_lookback - len(self.aux_qubits)

        if previous_round_lookback > 0:
            targets = [
                stim.target_rec(measurement_lookback),
                stim.target_rec(previous_round_lookback),
            ]
        else:
            targets = [stim.target_rec(measurement_lookback)]

        self.circuit.append(
            name=StimDecorators.DETECTOR,
            targets=targets,
            arg=tuple(list(qubit.identifiers) + [round]),
        )

    def measure_data_qubits_and_add_detectors(self):
        plaquette_detectors = self.z_auxiliary_qubits

        if self.logical_memory == "X":
            self.layer(OneQubitGates.H, self.data_qubits)
            plaquette_detectors = self.x_auxiliary_qubits

        self.apply(MeasurementGates.MZ, self.data_qubits)

        neighbours = [Qubit(-1, 1), Qubit(1, 1), Qubit(1, -1), Qubit(-1, -1)]
        data_qubit_lookback = -len(self.data_qubits)
        auxiliary_qubit_lookback = data_qubit_lookback - len(self.aux_qubits)

        for aux in plaquette_detectors:
            data_in_plaquette = [
                aux + neighbour
                for neighbour in neighbours
                if aux + neighbour in self.data_qubits
            ]
            self.circuit.append(
                StimDecorators.DETECTOR,
                [stim.target_rec(auxiliary_qubit_lookback + self.aux_qubits.index(aux))]
                + [
                    stim.target_rec(data_qubit_lookback + self.data_qubits.index(q))
                    for q in data_in_plaquette
                ],
                arg=tuple(list(aux.identifiers) + [self.rounds - 1]),
            )

    def add_logical(self):
        if self.logical_memory == "Z":
            self.circuit.append(
                StimDecorators.OBSERVABLE_INCLUDE,
                targets=[
                    stim.target_rec(-x)
                    for x in range(1, self.distance**2 - 1, self.distance)
                ],
                arg=0,
            )
        elif self.logical_memory == "X":
            self.circuit.append(
                StimDecorators.OBSERVABLE_INCLUDE,
                targets=[stim.target_rec(-x) for x in range(1, self.distance + 1)],
                arg=0,
            )

    def construct(self, interlaced: bool = True):
        detector_qubits = self.z_auxiliary_qubits
        if self.logical_memory == "X":
            self.layer(OneQubitGates.H, self.data_qubits)
            detector_qubits = self.x_auxiliary_qubits

        for round in range(self.rounds):
            self.syndrome_extraction_round(interlaced=interlaced)
            for qubit in detector_qubits:
                self.nth_round_detector(qubit=qubit, round=round)

        self.measure_data_qubits_and_add_detectors()

        self.add_logical()


if __name__ == "__main__":
    rplanar = RotatedPlanarCircuitBuilder(distance=3, rounds=1, logical_memory="Z")
    rplanar.construct(interlaced=False)
    print(rplanar.circuit)
    rplanar.circuit.detector_error_model()
    # rplanar.circuit.to_file("RotatedPlanar_d5_r5_XMem_HCNOT.txt")
