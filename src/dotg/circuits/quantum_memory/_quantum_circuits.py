"""This module generates noiseless quantum circuits."""
import warnings
from typing import Optional

import stim

# pylint: disable=no-member


class SurfaceCode:
    def __init__(self, *args, **kwargs):
        if args or kwargs:
            raise SyntaxError(
                "Can't make use of the top level surface code class, you must access one of the subclasses: Rotated or Unrotated."
            )

    class Rotated:
        def __init__(
            self, distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
        ) -> None:
            self.distance = distance
            self.rounds = rounds or distance
            self.memory_basis = memory_basis.lower()
            if self.memory_basis not in ["x", "Z"]:
                raise ValueError("Memory basis must be one of `X` or `Z`.")

        @property
        def circuit(self) -> stim.Circuit:
            return stim.Circuit.generated(
                code_task=f"surface_code:rotated_memory_{self.memory_basis}",
                distance=self.distance,
                rounds=self.rounds,
            ).flattened()

    class Unrotated:
        def __init__(
            self, distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
        ) -> None:
            self.distance = distance
            self.rounds = rounds or distance
            self.memory_basis = memory_basis.lower()
            if self.memory_basis not in ["x", "Z"]:
                raise ValueError("Memory basis must be one of `X` or `Z`.")

        @property
        def circuit(self) -> stim.Circuit:
            return stim.Circuit.generated(
                code_task=f"surface_code:unrotated_memory_{self.memory_basis}",
                distance=self.distance,
                rounds=self.rounds,
            ).flattened()


def rotated_surface_code(
    distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
) -> stim.Circuit:
    """Generate a stim circuit representing a rotated surface code without noise. The
    circuit is always flattened.

    Parameters
    ----------
    distance : int
        Code distance in both X and Z directions.
    rounds : int, optional
        Number of rounds to run the code for, by default None. If None, defaults
        to the code distance.
    memory_basis : str, optional
        Which logical memory to encode, by default Z. If anything other than
        'Z' or 'z' is passed, this defaults to the logical X memory.

    Returns
    -------
    stim.Circuit
        stim circuit object representing the code implementation.
    Raises
    ------
    warnings.warn
        User warning if the memory_basis argument is not recognised.
    """
    if memory_basis.lower() not in ["x", "z"]:
        warnings.warn(
            f"Memory basis kwarg not recoginised: {memory_basis}."
            " Defaulting to memory basis 'X'."
        )
    return stim.Circuit.generated(
        code_task="surface_code:rotated_memory"
        f"_{'x' if memory_basis.lower()!='z' else 'z'}",
        distance=distance,
        rounds=rounds or distance,
    ).flattened()


def unrotated_surface_code(
    distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
) -> stim.Circuit:
    """Generate a stim circuit representing a unrotated surface code without noise. The
    circuit is always flattened.

    Parameters
    ----------
    distance : int
        Code distance in both X and Z directions.
    rounds : int, optional
        Number of rounds to run the code for, by default None. If None, defaults
        to the code distance.
    memory_basis : str, optional
        Which logical memory to encode, by default Z. If anything other than
        'Z' or 'z' is passed, this defaults to the logical X memory.

    Returns
    -------
    stim.Circuit
        stim circuit object representing the code implementation.

    Raises
    ------
    warnings.warn
        User warning if the memory_basis argument is not recognised.
    """
    if memory_basis.lower() not in ["x", "z"]:
        warnings.warn(
            f"Memory basis kwarg not recoginised: {memory_basis}."
            " Defaulting to memory basis 'X'."
        )
    return stim.Circuit.generated(
        code_task="surface_code:unrotated_memory"
        f"_{'x' if memory_basis.lower()!='z' else 'z'}",
        distance=distance,
        rounds=rounds or distance,
    ).flattened()


def color_code(distance: int, rounds: Optional[int] = None) -> stim.Circuit:
    """Generate a stim circuit representing a color code without noise. The circuit is
    always flattened.

    Parameters
    ----------
    distance : int
        Code distance.
    rounds : int, optional
        Number of rounds to run the code for, by default None. If None, defaults
        to the code distance.

    Returns
    -------
    stim.Circuit
        stim circuit object representing the code implementation.
    """
    return stim.Circuit.generated(
        code_task="color_code:memory_xyz", distance=distance, rounds=rounds or distance
    ).flattened()
