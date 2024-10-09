"""This module provides a code family class for the color codes."""

from typing import Optional

import stim

from dotg.circuits._code_base_class import Code, CodeFamily


class ColorCode(CodeFamily):
    """Top level class for generating color code circuits. Current subclass is the
    Triangular color code."""

    class Triangular(Code):
        """Triangular color code class. After initialisation, access circuits for quantum
        memory and stability experiments with the `memory` and `stability` properties.

        Parameters
        ----------
        distance : int
            Code distance, must be odd.
        rounds : int, optional
            Number of rounds to run the code for, by default None. If None, defaults
            to the code distance.
        """

        def __init__(self, distance: int, rounds: Optional[int] = None) -> None:
            super().__init__(distance, rounds)
            if distance % 2 == 0:
                raise ValueError("Distance for the triangular color code must be odd.")

        @property
        def memory(self) -> stim.Circuit:
            return stim.Circuit.generated(
                code_task="color_code:memory_xyz",
                distance=self.distance,
                rounds=self.rounds,
            ).flattened()
