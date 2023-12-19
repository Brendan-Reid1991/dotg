"""Build a code object on a square grid of qubits."""
from typing import List, Dict


class Qubit:
    def __init__(self, *args) -> None:
        self.identifiers = tuple(args)

        self._iterator = (id for id in self.identifiers)

    def __add__(self, other):
        if not len(self.identifiers) == len(other.identifiers):
            raise ValueError("Can't add these two!")
        if len(self.identifiers) == 1:
            return Qubit(self.identifiers[0] + other.identifiers[0])
        return Qubit(*[x + y for x, y in zip(self.identifiers, other.identifiers)])

    def __repr__(self) -> str:
        _str = "Qubit(" + ", ".join(map(str, self.identifiers)) + ")"
        return _str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Qubit):
            return False
        return self.identifiers == other.identifiers

    def __hash__(self) -> int:
        return sum(hash(x) for x in self.identifiers)

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        return next(self._iterator)

    def __getitem__(self, index):
        return self.identifiers[index]


class SquareGridBuilder:
    def __init__(self, side_length: int) -> None:
        if side_length < 2:
            raise ValueError("Come on.")

        self.qubit_coordinates = sorted(
            [Qubit(x, y) for x in range(0, side_length) for y in range(0, side_length)],
            key=lambda x: (x[1], x[0]),
        )

        self._every_other_qubit = sorted(
            [
                Qubit(x, y)
                for x in range(1, side_length, 2)
                for y in range(1, side_length, 2)
            ],
            key=lambda x: (x[1], x[0]),
        )

        self.neighbours: Dict[str, List[Qubit]] = {
            "top_left_down": [Qubit(-1, 1), Qubit(-1, -1), Qubit(1, 1), Qubit(1, -1)],
            "top_left_right": [Qubit(-1, 1), Qubit(1, 1), Qubit(-1, -1), Qubit(1, -1)],
        }

    def neighbouring_sites(self, sequence: str):
        pass


if __name__ == "__main__":
    sg = SquareGridBuilder(11)
    print(sg._every_other_qubit)
    print(len(sg._every_other_qubit))
