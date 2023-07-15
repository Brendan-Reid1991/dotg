"""This module generates noiseless quantum circuits."""
from typing import Optional

import stim

# pylint: disable=no-member


def rotated_surface_code(
    distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
) -> stim.Circuit:
    """Generate a stim circuit representing a rotated surface code without noise.

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
    """
    return stim.Circuit.generated(
        code_task="surface_code:rotated_memory"
        f"_{'x' if memory_basis.lower()!='z' else 'z'}",
        distance=distance,
        rounds=rounds or distance
    )


def unrotated_surface_code(
    distance: int, rounds: Optional[int] = None, memory_basis: str = "Z"
) -> stim.Circuit:
    """Generate a stim circuit representing a unrotated surface code without noise.

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
    """
    return stim.Circuit.generated(
        code_task="surface_code:unrotated_memory"
        f"_{'x' if memory_basis.lower()!='z' else 'z'}",
        distance=distance,
        rounds=rounds or distance
    )


def color_code(distance: int, rounds: Optional[int] = None) -> stim.Circuit:
    """Generate a stim circuit representing a color code without noise.

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
    )
