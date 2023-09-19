"""This module provides base classes for code families and code members."""
from abc import ABC, abstractmethod
from typing import Optional

import stim


class CodeFamily(ABC):
    """Base class for code families."""

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            raise SyntaxError(
                f"Can't make use of the top level {self.__class__.__name__} class, you "
                "must access one of the subclasses."
            )


class Code(ABC):
    """Base class for subcodes."""

    def __init__(self, distance: int, rounds: Optional[int] = None) -> None:
        self.distance = distance
        self.rounds = rounds or distance

    @property
    @abstractmethod
    def memory(self) -> stim.Circuit:
        """Stim circuit representing a quantum memory experiment on this code without
        noise.

        Returns
        -------
        stim.Circuit
        """

    @property
    def stability(self) -> stim.Circuit:
        """Stim circuit representing a quantum stability experiment on this code without
        noise.

        Returns
        -------
        stim.Circuit
        """
        raise NotImplementedError("Stability experiments not yet implemented.")
