"""This module defines a class for qubit objects."""

from typing import ClassVar


class QubitCoordinate(tuple):
    """QubitCoordinate class.

    Subclassed from tuple, helpful for storing and tracking
    unique qubit indices during an experiment.

    Qubit index must be manually defined.

    If qubit was created via a QubitGrid call, the index should
    be defined automatically.

    Properties
    ----------
    x: float
        The x-coordinate of this qubit.
    y: float
        The y-coordinate of this qubit.
    idx: int
        The index given to this qubit, by default None.
    """

    x: ClassVar[float]
    y: ClassVar[float]

    def __new__(cls, x, y):
        instance = super().__new__(cls, (x, y))
        instance._idx = None
        instance.x = x
        instance.y = y
        return instance

    @property
    def idx(self) -> int:
        return self._idx

    @idx.setter
    def idx(self, value):
        self._idx = value

    def __add__(self, alt):
        if len(alt) > 2:
            raise ValueError(f"Coordinates should all be of size 2. Received {alt}")
        return QubitCoordinate(self[0] + alt[0], self[1] + alt[1])
