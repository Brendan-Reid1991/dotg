from typing import Optional
import numpy as np
from enum import Enum
import ast
import matplotlib
import matplotlib.pyplot as plt

from builder.utilities import QubitCoordinate


class HexagonalGrid:
    """A hexagonal grid structure, used to define the triangular
    color code.

    Parameters
    ----------
    x_lim: int
        The max x-coordinate on the grid.
    y_lim: int
        The max y-coordinate on the grid.

    Attributes
    ----------
    data_qubits: list[QubitCoordinate]
        A list of data qubits defined on the grid.
    z_stabilizers: list[QubitCoordinate]
        A list of Z stabilizers defined on the grid.
    x_stabilizers: list[QubitCoordinate]
        A list of X stabilizers defined on the grid.
    coordinate_mapping: dict[QubitCoordinate, int]
        A dictionary that maps a qubit coordinate to its index.
    schedules: dict[str, list[SquareGrid.Displacer]]
        Default schedules for X and Z syndrome extraction circuits,
        accessed by schedules['x'] and schedules['z'] respectively.
        Values of these keys are the time-step indexed interaction
        order, i.e.
        >>> schedules['x'] = [SquareGrid.Displacer.TOP_LEFT,
                            SquareGrid.Displacer.TOP_RIGHT,
                            SquareGrid.Displacer.BOTTOM_LEFT,
                            SquareGrid.Displacer.BOTTOM_RIGHT]
        The elements of this list can be added to an X stabilizer
        qubit to determine which data qubit it should interact with
        in that timestep.
    """

    class Displacer(Enum):
        NE: tuple[float, float] = (0.5, 1)
        E: tuple[float, float] = (1, 0)
        SE: tuple[float, float] = (0.5, -1)
        SW: tuple[float, float] = (-0.5, -1)
        W: tuple[float, float] = (-1, 0)
        NW: tuple[float, float] = (-0.5, 1)

    def __init__(self, x_lim: int, y_lim: int) -> None:
        self._x_lim = x_lim
        self._y_lim = y_lim

        if not (self._x_lim - 1) % 3 == 0 and (self._y_lim - 1) % 3 == 0:
            raise ValueError(
                f"""Invalid dimensions for the hexagonal grid.
                Received {(self._x_lim, self._y_lim)} but dimensions 
                must satisfy the conditon (x - 1)mod3 = 0."""
            )

        (
            self.data_qubits,
            self.red_qubits,
            self.blue_qubits,
            self.green_qubits,
            self.coordinate_mapping,
        ) = self._initialize()

    def _get_data_qubits(self) -> list[QubitCoordinate]:
        """Get the data qubits on the grid.

        Returns
        -------
        list[QubitCoordinate]
        """
        return [
            QubitCoordinate(x, y)
            for x in range(0, self._x_lim + 1)
            for y in range(0, self._y_lim + 1)
        ]

    def _get_red_stabilizer_qubits(self) -> list[QubitCoordinate]:
        """Get the red stabilizer qubits.

        Returns
        -------
        list[QubitCoordinate]
        """
        return sorted(
            self._add_bulk_stabilizers(
                [QubitCoordinate(x, 0) for x in np.arange(1, self._x_lim, 3)]
            ),
            key=lambda x: x[1],
        )

    def _get_blue_stabilizer_qubits(self) -> list[QubitCoordinate]:
        """Get the red stabilizer qubits.

        Returns
        -------
        list[QubitCoordinate]
        """
        return sorted(
            self._add_bulk_stabilizers(
                [QubitCoordinate(x, 1) for x in np.arange(2.5, self._x_lim, 3)]
            ),
            key=lambda x: x[1],
        )

    def _get_green_stabilizer_qubits(self) -> list[QubitCoordinate]:
        """Get the green stabilizer qubits.

        Returns
        -------
        list[QubitCoordinate]
        """
        return sorted(
            self._add_bulk_stabilizers(
                [QubitCoordinate(x, 2) for x in np.arange(1, self._x_lim, 3)]
            ),
            key=lambda x: x[1],
        )

    def _add_bulk_stabilizers(
        self, colored_stabilizers: list[QubitCoordinate]
    ) -> list[QubitCoordinate]:
        """Add bulk stabilizers to a list of colored stabilizers,
        by stepping across the hexagonal lattice in a measured fashion.

        Parameters
        ----------
        colored_stabilizers : list[QubitCoordinate]
            A list of initial colored stabilizers.

        Returns
        -------
        list[QubitCoordinate]
            A list of more stabilizers of the same color.
        """

        _valid = lambda q: (0 <= q.x < self._x_lim and 0 <= q.y < self._y_lim)

        def _search_grid(
            qubit: QubitCoordinate, valid_grab_bag: list[QubitCoordinate]
        ) -> list[QubitCoordinate]:
            look_left: float = -1.5
            q = qubit + (look_left, 3)
            if _valid(q):
                valid_grab_bag.append(q)
                valid_grab_bag = _search_grid(qubit=q, valid_grab_bag=valid_grab_bag)

            look_right: float = 1.5
            q = qubit + (look_right, 3)
            if _valid(q):
                valid_grab_bag.append(q)
                valid_grab_bag = _search_grid(qubit=q, valid_grab_bag=valid_grab_bag)

            return valid_grab_bag

        additions: list[QubitCoordinate] = []
        for qubit in colored_stabilizers:
            additions += _search_grid(qubit=qubit, valid_grab_bag=additions)

        return list(set(colored_stabilizers + additions))

    def _get_neighbour(
        self, qubit: QubitCoordinate, displacer: Displacer
    ) -> QubitCoordinate | None:
        """Given a qubit coordinate and a displacement, get
        the neighbouring qubit if it exists.

        Parameters
        ----------
        qubit : QubitCoordinate
            Qubit to check neighbours of.
        displacer : Displacer
            A displacement to look for another qubit.

        Returns
        -------
        QubitCoordinate | None
            A qubit coordinate or None, if no qubit exists at
            that displacement.
        """
        neighbour = qubit + displacer
        try:
            return next(q for q in self.data_qubits if q == neighbour)
        except StopIteration:
            return None

    def stabilizer_data_qubit_groups(
        self, stabilizer: QubitCoordinate
    ) -> list[QubitCoordinate]:
        """Given a stabilizer qubit, return a list of
        the data qubits incident on the stabilizer.

        Parameters
        ----------
        stabilizer : QubitCoordinate
            Which stabilizer to consider.

        Returns
        -------
        list[QubitCoordinate]
            List of data qubits incident on the stabilizer.
        """
        return [
            q
            for displacement in HexagonalGrid.Displacer._value2member_map_
            if (q := self._get_neighbour(stabilizer, displacement))
        ]

    def _initialize(
        self,
    ) -> tuple[
        list[QubitCoordinate],
        list[QubitCoordinate],
        list[QubitCoordinate],
        list[QubitCoordinate],
        dict[QubitCoordinate, int],
    ]:
        """Initialize the grid.

        Returns
        -------
        tuple[ list[QubitCoordinate],
                list[QubitCoordinate],
                list[QubitCoordinate],
                list[QubitCoordinate],
                dict[QubitCoordinate, int] ]
            In order:
            - List of data qubits
            - List of RED stabilizers
            - List of BLUE stabilizers
            - List of GREEN stabilizers
            - Qubit coordinate to qubit index dictionary.
        """
        red_qubits = self._get_red_stabilizer_qubits()
        blue_qubits = self._get_blue_stabilizer_qubits()
        green_qubits = self._get_green_stabilizer_qubits()
        data_qubits = [
            q
            for y in range(0, self._y_lim)
            for x in np.arange(0 if y % 2 == 0 else 0.5, self._x_lim)
            if (q := QubitCoordinate(x, y))
            not in red_qubits + blue_qubits + green_qubits
        ]
        coordinate_mapping: dict[QubitCoordinate, int] = {}
        for idx, qubit in enumerate(
            data_qubits + red_qubits + blue_qubits + green_qubits
        ):
            qubit.idx = idx
            coordinate_mapping[qubit] = idx

        return data_qubits, red_qubits, blue_qubits, green_qubits, coordinate_mapping
