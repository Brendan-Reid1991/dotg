"""This module provides a code family class for the surface codes."""
from typing import Optional, List, Union

import stim

from dotg.circuits._code_base_class import Code, CodeFamily
from dotg.utilities.stim_assets import (
    OneQubitGates,
    TwoQubitGates,
    ResetGates,
    MeasurementGates,
    StimDecorators,
)


class SurfaceCodeSubClass(Code):
    """A base class for surface codes. Adds an extra check on the memory basis being
    considered."""

    def __init__(
        self, distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
    ) -> None:
        super().__init__(distance, rounds)
        self.memory_basis = memory_basis.lower()
        if self.memory_basis not in ["x", "z"]:
            raise ValueError("Memory basis must be one of `X` or `Z`.")


class SurfaceCode(CodeFamily):
    """Top level class for generating surface code circuits. Current subclasses are
    Rotated and Unrotated.

    # TODO Add XZZX and XY Codes.
    """

    class Rotated(SurfaceCodeSubClass):
        """Rotated surface code class. After initialisation, access circuits for quantum
        memory and stability experiments with the `memory` and `stability` properties.
        Parameters
        ----------
        distance : int
            Code distance in both X and Z directions.
        rounds : int, optional
            Number of rounds to run the code for, by default None. If None, defaults
            to the code distance.
        memory_basis : str, optional
            Which logical memory to encode, by default Z.

        Raises
        ------
        ValueError
            If memory_basis kwarg is not one of X, x, Z or z.
        """

        def __init__(
            self, distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
        ) -> None:
            super().__init__(
                distance=distance, rounds=rounds, memory_basis=memory_basis
            )

        @property
        def memory(self) -> stim.Circuit:
            return stim.Circuit.generated(
                code_task=f"surface_code:rotated_memory_{self.memory_basis}",
                distance=self.distance,
                rounds=self.rounds,
            ).flattened()

        @property
        def stability(self) -> stim.Circuit:
            stability_circuit = stim.Circuit()
            qubits = list(range(9))
            data_qubits = list(range(4))
            x_aux = [4]
            z_aux = [5, 6, 7, 8]
            layers = [
                [4, 2, 6, 3, 5, 0],
                [4, 3, 6, 1, 7, 2],
                [4, 0, 5, 1, 8, 2],
                [4, 1, 8, 0, 7, 3],
            ]

            def time_step():
                return stability_circuit.append("TICK")

            def reset(qubits: List[int]):
                stability_circuit.append(name=ResetGates.RZ, targets=qubits)

            def measure(qubits: List[int]):
                stability_circuit.append(name=MeasurementGates.MZ, targets=qubits)

            def gate(gate: Union[OneQubitGates, TwoQubitGates], qubits: List[int]):
                stability_circuit.append(name=gate, targets=qubits)

            def syndrome_extraction():
                for layer in layers:
                    gate(TwoQubitGates.CX, layer)
                    time_step()

            for _qubit in qubits:
                stability_circuit.append(
                    name=StimDecorators.QUBIT_COORDS, targets=_qubit, arg=_qubit
                )

            reset(qubits=qubits)
            time_step()
            gate(OneQubitGates.H, x_aux + data_qubits)
            time_step()
            syndrome_extraction()
            gate(OneQubitGates.H, x_aux)
            time_step()
            measure(z_aux + x_aux)
            stability_circuit.append(
                StimDecorators.DETECTOR,
                stim.target_rec(-1),
            )

            lookback = 5
            for _ in range(1, self.rounds):
                reset(qubits=x_aux + z_aux)
                time_step()
                gate(OneQubitGates.H, x_aux)
                time_step()
                syndrome_extraction()
                gate(OneQubitGates.H, x_aux)
                time_step()
                measure(z_aux + x_aux)
                for idx, qubit in enumerate((z_aux + x_aux)[::-1], start=1):
                    stability_circuit.append(
                        StimDecorators.DETECTOR,
                        [
                            stim.target_rec(-idx),
                            stim.target_rec(-idx - lookback),
                        ],
                        # (qubit, _),÷
                    )
                # for idz, z_aux in enumerate(z_aux):
                #     stability_circuit.append(StimDecorators.DETECTOR, [stim.target_rec])

            gate(OneQubitGates.H, data_qubits)
            time_step()
            measure(data_qubits)
            stability_circuit.append(
                StimDecorators.DETECTOR,
                [
                    stim.target_rec(-1),
                    stim.target_rec(-2),
                    stim.target_rec(-3),
                    stim.target_rec(-4),
                    stim.target_rec(-5),
                ],
                # (qubit, self.rounds),
            )

            stability_circuit.append(
                StimDecorators.OBSERVABLE_INCLUDE,
                [
                    stim.target_rec(-6),
                    stim.target_rec(-7),
                    stim.target_rec(-8),
                    stim.target_rec(-9),
                ],
                (0),
            )
            return stability_circuit

    class Unrotated(SurfaceCodeSubClass):
        """Unrotated surface code class. After initialisation, access circuits for quantum
        memory and stability experiments with the `memory` and `stability` properties.

        Parameters
        ----------
        distance : int
            Code distance in both X and Z directions.
        rounds : int, optional
            Number of rounds to run the code for, by default None. If None, defaults
            to the code distance.
        memory_basis : str, optional
            Which logical memory to encode, by default Z.

        Raises
        ------
        ValueError
            If memory_basis kwarg is not one of X, x, Z or z.
        """

        def __init__(
            self, distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
        ) -> None:
            super().__init__(
                distance=distance, rounds=rounds, memory_basis=memory_basis
            )

        @property
        def memory(self) -> stim.Circuit:
            return stim.Circuit.generated(
                code_task=f"surface_code:unrotated_memory_{self.memory_basis}",
                distance=self.distance,
                rounds=self.rounds,
            ).flattened()
