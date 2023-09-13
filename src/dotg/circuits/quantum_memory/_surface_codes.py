"""This module generates noiseless quantum circuits."""
import warnings
from typing import Optional
import stim

from dotg.circuits.quantum_memory._code_base_class import _Code, _CodeFamily


class _SurfaceCodeSubClass(_Code):
    """A base class for surface codes. Adds an extra check on the memory basis being considered."""

    def __init__(
        self, distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
    ) -> None:
        super().__init__(distance, rounds)
        self.memory_basis = memory_basis.lower()
        if self.memory_basis not in ["x", "z"]:
            raise ValueError("Memory basis must be one of `X` or `Z`.")


class SurfaceCode(_CodeFamily):
    """Top level class for generating surface code circuits. Current subclasses are Rotated and Unrotated.

    # TODO Add XZZX and XY Codes.
    """

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            raise SyntaxError(
                "Can't make use of the top level surface code class, you must access one of the subclasses: Rotated or Unrotated."
            )

    class Rotated(_SurfaceCodeSubClass):
        """Rotated surface code class. After initialisation, access the circuit representing the code experiment with the `circuit` property.

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
            super().__init__(distance=distance, rounds=rounds, memory_basis=memory_basis)

        @property
        def circuit(self) -> stim.Circuit:
            """Stim circuit representing a rotated surface code instance

            Returns
            -------
            stim.Circuit
            """
            return stim.Circuit.generated(
                code_task=f"surface_code:rotated_memory_{self.memory_basis}",
                distance=self.distance,
                rounds=self.rounds,
            ).flattened()

    class Unrotated(_SurfaceCodeSubClass):
        """Unrotated surface code class. After initialisation, access the circuit representing the code experiment with the `circuit` property.

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
            super().__init__(distance=distance, rounds=rounds, memory_basis=memory_basis)

        @property
        def circuit(self) -> stim.Circuit:
            return stim.Circuit.generated(
                code_task=f"surface_code:unrotated_memory_{self.memory_basis}",
                distance=self.distance,
                rounds=self.rounds,
            ).flattened()
