"""The SquareGrid class: helpful for tracking qubit coordinates and indices
on square grid architectures."""

from enum import Enum

from builder.utilities._qubit_coordinate import QubitCoordinate


class SquareGrid:
    """Define a square grid of qubits.

    At present, this class is used to build the rotated surface code only.

    Data qubits are placed on integer nodes, so (1, 1), (2, 3) etc.
    (1, 1) is always the first data qubit and always has index 0.

    X- and Z-stabilizers are placed on the (x.5, y.5) nodes,
    where an X stabilizer is always defined to
    be placed on (1.5, 0.5).

    As a rule then, if an X stabilizer has coordinates (i, j):
    >>> 1.5  <= i <= self._x_lim - 0.5
    >>> 0.5 <= j <= self._y_lim + 0.5

    If a Z-stabilizer has coordinates (i, j):
    >>> 0.5 <= i <= self._x_lim + 0.5
    >>> 1.5 <= j <= self._y_lim - 0.5

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
        """Displacement tuples for checking the neighbours
        of stabilizer qubits.

        Defined only to avoid user error.
        """

        TOP_RIGHT = (0.5, 0.5)
        TOP_LEFT = (-0.5, 0.5)
        BOTTOM_RIGHT = (0.5, -0.5)
        BOTTOM_LEFT = (-0.5, -0.5)

    def __init__(self, x_lim: int, y_lim: int) -> None:
        self._x_lim = x_lim
        self._y_lim = y_lim

        (
            self.data_qubits,
            self.x_stabilizers,
            self.z_stabilizers,
            self.coordinate_mapping,
        ) = self._initialize()

        self.schedules: dict[str, list[SquareGrid.Displacer]] = {
            "x": [
                SquareGrid.Displacer.TOP_LEFT,
                SquareGrid.Displacer.TOP_RIGHT,
                SquareGrid.Displacer.BOTTOM_LEFT,
                SquareGrid.Displacer.BOTTOM_RIGHT,
            ],
            "z": [
                SquareGrid.Displacer.TOP_LEFT,
                SquareGrid.Displacer.BOTTOM_LEFT,
                SquareGrid.Displacer.TOP_RIGHT,
                SquareGrid.Displacer.BOTTOM_RIGHT,
            ],
        }

    def _get_neighbour(
        self, qubit: QubitCoordinate, displacer: Displacer
    ) -> QubitCoordinate | None:
        """Given a qubit coordinate and a displacement,
        get the neighbour of the qubit.

        self._get_neighbour(
            qubit=QubitCoordinate(1.5, 0.5),
            displacer=Displacement.TOP_LEFT
        )
        >>> QubitCoordinate(1, 1)

        Parameters
        ----------
        stabilizer_q : QubitCoordinate
            Stabilizer qubit coordinate.
        displacer : Displacer
            Displacement operator.


        Returns
        -------
        QubitCoordinate | None
            Returns a qubit coordinate
        """
        neighbour = qubit + displacer.value
        try:
            idx = self.coordinate_mapping[neighbour]
        except KeyError:
            return None
        return next(key for key, val in self.coordinate_mapping.items() if val == idx)

    def stabilizer_data_qubit_groups(
        self, stabilizer: QubitCoordinate
    ) -> list[QubitCoordinate]:
        """For a given stabilizer, return the list of data qubits in its neighbourhood.

        Parameters
        ----------
        stabilizer : QubitCoordinate
            Which stabilizer to consider.

        Returns
        -------
        list[QubitCoordinate]
            A list of data qubits in the stabilizers neighbourhood.
        """

        schedule = (
            self.schedules["x"]
            if stabilizer in self.x_stabilizers
            else self.schedules["z"]
        )

        return [
            x
            for x in map(self._get_neighbour, [stabilizer] * len(schedule), schedule)
            if x
        ]

    def _get_data_qubits(self) -> list[QubitCoordinate]:
        """Get the data qubits on the grid.

        Returns
        -------
        list[QubitCoordinate]
        """
        return sorted(
            [
                QubitCoordinate(x, y)
                for x in range(1, self._x_lim)
                for y in range(1, self._y_lim)
            ],
            key=lambda x: (x[0], x[1]),
        )

    def _get_x_stabilizers(self) -> list[QubitCoordinate]:
        """Get a list of all the X stabilizers in the grid.

        Patches are always orientated with a weight-2
        X stabilizer at the bottom left hand corner of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """
        return sorted(
            [
                QubitCoordinate(i + 0.5, j + 0.5)
                for j in range(0, self._y_lim)
                for i in range(1 if j % 2 == 0 else 0, self._x_lim, 2)
                if (i, j)
                not in [
                    (0, 0),
                    (0, self._y_lim - 1),
                    (self._x_lim - 1, 0),
                    (self._x_lim - 1, self._y_lim - 1),
                ]
            ],
            key=lambda x: (x[0], x[1]),
        )

    def _get_z_stabilizers(self) -> list[QubitCoordinate]:
        """Get a list of all the Z stabilizers in the grid.

        Returns
        -------
        list[QubitCoordinate]
        """
        return sorted(
            [
                QubitCoordinate(i + 0.5, j + 0.5)
                for j in range(0, self._y_lim)
                for i in range(0 if j % 2 == 0 else 1, self._x_lim, 2)
                if (i, j)
                not in [
                    (0, 0),
                    (0, self._y_lim - 1),
                    (self._x_lim - 1, 0),
                    (self._x_lim - 1, self._y_lim - 1),
                ]
            ],
            key=lambda x: (x[0], x[1]),
        )

    def _initialize(
        self,
    ) -> tuple[
        list[QubitCoordinate],
        list[QubitCoordinate],
        list[QubitCoordinate],
        dict[QubitCoordinate, int],
    ]:
        """Initialize the data qubits, X stabilizers and Z stabilizers.

        Also define the coordinate mapping between coordinates and indices.

        Returns
        -------
        tuple[
            list[QubitCoordinate],
            list[QubitCoordinate],
            list[QubitCoordinate],
            dict[QubitCoordinate, int]]
        """
        data_qubits = self._get_data_qubits()
        x_stabilizers = self._get_x_stabilizers()
        z_stabilizers = self._get_z_stabilizers()

        coordinate_mapping: dict[QubitCoordinate, int] = {
            coord: idx
            for idx, coord in enumerate(data_qubits + x_stabilizers + z_stabilizers)
        }

        for coord, idx in coordinate_mapping.items():
            coord.idx = idx

        return data_qubits, x_stabilizers, z_stabilizers, coordinate_mapping


if __name__ == "__main__":
    grid = SquareGrid(4, 4)
    print(grid.data_qubits)
    print(grid.x_stabilizers)
