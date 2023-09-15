from typing import Optional
import stim

from abc import ABC, abstractproperty


class _CodeFamily(ABC):
    """Base class for code families."""

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            raise SyntaxError(
                f"Can't make use of the top level {self.__class__.__name__} class, you "
                "must access one of the subclasses."
            )


class _Code(ABC):
    """Base class for subcodes."""

    def __init__(self, distance: int, rounds: Optional[int] = None) -> None:
        self.distance = distance
        self.rounds = rounds or distance

    @abstractproperty
    def circuit(self) -> stim.Circuit:
        """Stim circuit representing the code experiment without noise.

        Returns
        -------
        stim.Circuit
        """
