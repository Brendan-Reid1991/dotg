"""The HexagonalGrid class: helpful for tracking qubit coordinates and indices
on hexagonal architectures."""

from enum import Enum
import numpy as np

from builder.utilities import QubitCoordinate


# pylint: disable=protected-access


class HexagonalGrid:
    """A hexagonal grid structure, where qubits exist on a weight-3 connectivity
    graph.

    Qubit at coordinate (1,1) is always a data qubit, and always has index 0.
    In order, data qubits are indexed first. Then red plaquette qubits,
    then blue, then green.

    Parameters
    ----------
    x_lim : int
        The max x-coordinate on the grid. Must satisfy the condition that
        (x_lim-1)mod3 == 0
    y_lim : int
        The max y-coordinate on the grid. Must satisfy the condition that
        (y_lim-1)mod3 == 0

    Attributes
    ----------
    data_qubits: list[QubitCoordinate]
        A list of data qubit coordinates on the grid.
    red_qubits: list[QubitCoordinate]
        A list of qubits on red-colored plaquettes.
    blue_qubits: list[QubitCoordinate]
        A list of qubits on blue-colored plaquettes.
    green_qubits: list[QubitCoordinate]
        A list of qubits on green-colored plaquettes.
    schedules: dict[str, list[HexagonalGrid.Displacer]]
        A dictionary of schedules for red, blue and green plaquettes.
        At present, they each have the same schedule which is clockwise
        starting at the SW qubit.
    coordinate_mapping: dict[QubitCoordinate, int]
        A map from the qubit coordinate and its corresponding index.


    Raises
    ------
    ValueError
        If the given x_lim, y_lim args do not satisfy the condition that
        (h-1)mod3 == 0 for h=x_lim and h=y_lim.

    """

    class Displacer(Enum):
        """The displacer for the hexagonal grid.

        Indicates the steps taken from any given qubit to search it's neighbourhood.
        """

        NE: tuple[float, float] = (0.5, 1)
        E: tuple[float, float] = (1, 0)
        SE: tuple[float, float] = (0.5, -1)
        SW: tuple[float, float] = (-0.5, -1)
        W: tuple[float, float] = (-1, 0)
        NW: tuple[float, float] = (-0.5, 1)

    def __init__(self, x_lim: int, y_lim: int) -> None:
        self._x_lim = x_lim
        self._y_lim = y_lim

        if not (self._x_lim - 1) % 3 == 0 or not (self._y_lim - 1) % 3 == 0:
            raise ValueError(
                f"""Invalid dimensions for the hexagonal grid.
                Received {(self._x_lim, self._y_lim)} but dimensions 
                must satisfy the conditon (h - 1)mod3 = 0."""
            )

        (
            self.data_qubits,
            self.red_qubits,
            self.blue_qubits,
            self.green_qubits,
            self.coordinate_mapping,
        ) = self._initialize()

        self.schedules: dict[str, list[HexagonalGrid.Displacer]] = {
            "red": [
                HexagonalGrid.Displacer.SW,
                HexagonalGrid.Displacer.W,
                HexagonalGrid.Displacer.NW,
                HexagonalGrid.Displacer.NE,
                HexagonalGrid.Displacer.E,
                HexagonalGrid.Displacer.SE,
            ],
            "blue": [
                HexagonalGrid.Displacer.SW,
                HexagonalGrid.Displacer.W,
                HexagonalGrid.Displacer.NW,
                HexagonalGrid.Displacer.NE,
                HexagonalGrid.Displacer.E,
                HexagonalGrid.Displacer.SE,
            ],
            "green": [
                HexagonalGrid.Displacer.SW,
                HexagonalGrid.Displacer.W,
                HexagonalGrid.Displacer.NW,
                HexagonalGrid.Displacer.NE,
                HexagonalGrid.Displacer.E,
                HexagonalGrid.Displacer.SE,
            ],
        }

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

        def _valid(qubit: QubitCoordinate) -> bool:
            """Determine if a given qubit coordinate is valid, in that it is within
            the confines of the grid.

            Parameters
            ----------
            qubit : QubitCoordinate
                Qubit coordinate.

            Returns
            -------
            bool
                True if it is valid, False otherwise.
            """
            return 0 <= qubit.x < self._x_lim and 0 <= qubit.y < self._y_lim

        def _search_grid(
            qubit: QubitCoordinate, valid_grab_bag: list[QubitCoordinate]
        ) -> list[QubitCoordinate]:
            """Search the grid recursively, adding valid additional qubits
            as we go.

            This function takes in a qubit coordinate, which should either a red,
            blue or green stabilizer. It then "looks left" and "looks right" by
            moving 1.5 cells to the left or right, and 3 cells up. This should be another
            stabilizer of the same color.

            If it is a valid stabilizer, this function is called recursively from this
            new qubit.

            Parameters
            ----------
            qubit : QubitCoordinate
                Qubit coordinate to start from.
            valid_grab_bag : list[QubitCoordinate]
                List of valid additional qubits.

            Returns
            -------
            list[QubitCoordinate]
                The valid_grab_bag variable, possibly with new entries.
            """
            look_left: float = -1.5
            new_qubit = qubit + (look_left, 3)
            if _valid(new_qubit):
                valid_grab_bag.append(new_qubit)
                valid_grab_bag = _search_grid(
                    qubit=new_qubit, valid_grab_bag=valid_grab_bag
                )

            look_right: float = 1.5
            new_qubit = qubit + (look_right, 3)
            if _valid(new_qubit):
                valid_grab_bag.append(new_qubit)
                valid_grab_bag = _search_grid(
                    qubit=new_qubit, valid_grab_bag=valid_grab_bag
                )

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
            qubit
            for displacement in HexagonalGrid.Displacer._value2member_map_
            if (qubit := self._get_neighbour(stabilizer, displacement))
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
            qubit
            for y in range(0, self._y_lim)
            for x in np.arange(0 if y % 2 == 0 else 0.5, self._x_lim)
            if (qubit := QubitCoordinate(x, y))
            not in red_qubits + blue_qubits + green_qubits
        ]
        coordinate_mapping: dict[QubitCoordinate, int] = {}
        for idx, qubit in enumerate(
            data_qubits + red_qubits + blue_qubits + green_qubits
        ):
            qubit.idx = idx
            coordinate_mapping[qubit] = idx

        return data_qubits, red_qubits, blue_qubits, green_qubits, coordinate_mapping
