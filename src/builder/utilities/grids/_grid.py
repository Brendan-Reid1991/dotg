"""A base class for qubit grids."""

from abc import abstractmethod
from typing import TypeAlias, TypeVar
from builder.utilities._qubit_coordinate import QubitCoordinate

# Displacer: TypeAlias = tuple[float, float]
Displacer = TypeVar("Displacer")


class QubitGrid:
    """A simple base class for qubit grids."""

    def __init__(self, *args, **kwargs) -> None:
        self._data_qubits: list[QubitCoordinate] = []
        self._coord_to_index_map: dict[QubitCoordinate, int] = {}

    @property
    def data_qubits(self) -> list[QubitCoordinate]:
        """Get a list of the data qubits in the grid.

        Returns
        -------
        list[QubitCoordinate]
            Data qubits in the grid.

        Raises
        ------
        ValueError
            If the attribute has not been set correctly.
        """
        if not self._data_qubits:
            raise ValueError(
                f"""Grid class {self.__class__.__name__} must allocate an attribute
                data_qubits."""
            )
        return self._data_qubits

    @data_qubits.setter
    def data_qubits(self, updated_list_of_data_qubits: list[QubitCoordinate]) -> None:
        self._data_qubits = updated_list_of_data_qubits

    @property
    def coordinate_mapping(self) -> dict[QubitCoordinate, int]:
        """A map from qubit coordinates to qubit indices.

        Returns
        -------
        dict[QubitCoordinate, int]

        Raises
        ------
        ValueError
            If the property has not been instantiated.
        """
        if not self._coord_to_index_map:
            raise ValueError(
                f"""Grid class {self.__class__.__name__} must allocate an attribute
                coordinate_mapping."""
            )
        return self._coord_to_index_map

    @coordinate_mapping.setter
    def coordinate_mapping(self, updated_map: dict[QubitCoordinate, int]) -> None:
        self._coord_to_index_map = updated_map

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
        neighbour = qubit + displacer  # type: ignore
        try:
            return next(q for q in self.data_qubits if q == neighbour)
        except StopIteration:
            return None

    @abstractmethod
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
        pass
