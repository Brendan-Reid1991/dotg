"""This module defines PauliProduct, a subclass of the str object."""

from __future__ import annotations
import re
from ast import literal_eval
from collections import defaultdict

import stim


class PauliProduct(str):
    """A special string class for Pauli products.

    Pauli products take the form {Pauli}{qubit_index} and are separated by '.',
    for example: X0.Y1.Z12.X20

    Inputs must take the above format, or be a stim.PauliString object.

    Attributes
    ----------
    indices: list[int]
        A list of the qubit indices involved in the Pauli product.
        E.g.
        >>> PauliProduct(X0.Y1.Z12.X20).indices
        [0, 1, 12, 20]
    pauli_terms: list[str]
        A list of the Pauli terms present in the Pauli product.
        E.g.
        >>> PauliProduct(X0.Y1.Z12.X20).pauli_terms
        ['X', 'Y', 'Z', 'X']
    index_to_pauli_map: Dict[int, str]
        A dictionary with indices as keys and Pauli terms as values.
        E.g.
        >>> PauliProduct(X0.Y1.Z12.X20).index_to_pauli_map
        {0: 'X', 1: 'Y', 12: 'Z', 20: 'X'}
    """

    sign = "+"

    def __new__(cls, string: str | stim.PauliString):
        """Create a new PauliProduct. If it is a stim.PauliString, convert it
        into the correct format and then validate it's structure.

        Parameters
        ----------
        string : str | stim.PauliString
            String representing the Pauli product.
        """
        if isinstance(string, stim.PauliString):
            string = ".".join(
                [
                    f"{char}{idx}"
                    for idx, char in enumerate(str(string)[1:])
                    if char.isalpha()
                ]
            )
        instance = super().__new__(cls, string.upper())
        if string == "":
            return instance

        instance._validate()
        instance = super().__new__(cls, instance._condense())
        return instance

    def _validate(self) -> None:
        r"""Ensure that all entries in the string follow the pattern of {Pauli
        {qubit_index}, separated by '.'

        Raises
        ------
        ValueError
            If any entry does not match the regex pattern '[X-Z]\d+'.
        """
        individual_pauli_products = self.split(".")
        if not all(
            re.fullmatch(r"[X-Z]\d+", conjugation)
            for conjugation in individual_pauli_products
        ):
            raise ValueError(
                f"""Some entries do not follow the correct pattern for a Pauli 
                product.\n    {individual_pauli_products}"""
            )

    def _condense(self) -> str:
        """This function is used to condense Pauli product strings that have
        multiple Paulis attached to the same index.

        E.g.
        >>> X0.Y0.X1.X1.Z1.X2

        would be condensed to
        >>> Z0.Z1.X2


        Returns
        -------
        str
            Condensed version of the input string.
        """
        X = "X"
        Y = "Y"
        Z = "Z"
        pauli_product_map: dict[tuple[str, ...], str] = {
            (X, Z): Y,
            (X, Y): Z,
            (Y, X): Z,
            (Y, Z): X,
            (Z, X): Y,
            (Z, Y): X,
        }
        paulis_on_index: dict[int, list[str]] = defaultdict(list)
        for entry in self.split("."):
            pauli_term = "".join([p for p in entry if p.isalpha()])
            index = literal_eval("".join([i for i in entry if i.isnumeric()]))
            paulis_on_index[index].append(pauli_term)

        condensed = []
        qubit_index: int
        pauli_terms: list[str]
        for qubit_index, pauli_terms in paulis_on_index.items():
            odd_parity_paulis: tuple[str, ...] = tuple(
                [p for p in pauli_terms if pauli_terms.count(p) % 2 != 0]
            )
            if len(odd_parity_paulis) == 1:
                condensed.append(f"{odd_parity_paulis[0]}{qubit_index}")
            if len(odd_parity_paulis) == 2:
                condensed.append(f"{pauli_product_map[odd_parity_paulis]}{qubit_index}")
        return ".".join(sorted(condensed, key=lambda x: literal_eval(x[1:])))

    def __add__(self, other: str | PauliProduct) -> PauliProduct:
        return PauliProduct(".".join(self.split(".") + other.split(".")))

    def __repr__(self):
        return self.sign + self

    def __str__(self):
        return self.sign + self

    @property
    def indices(self) -> list[int]:
        """Get the qubit indices from the Pauli product.

        Returns
        -------
        list[int]
        """
        if len(self) == 0:
            return []
        return [
            literal_eval(index)
            for entry in self.split(".")
            for index in ["".join(str_val for str_val in entry if str_val.isnumeric())]
        ]

    @property
    def pauli_terms(self) -> list[str]:
        """Get the Pauli terms from the Pauli product.

        Returns
        -------
        list[str]
        """
        return [
            index
            for entry in self.split(".")
            for index in ["".join(str_val) for str_val in entry if str_val.isalpha()]
        ]

    @property
    def index_to_pauli_map(self) -> dict[int, str]:
        """A dictionary where keys are qubit indices and values are the Pauli terms.

        Returns
        -------
        Dict[int, str]
        """
        return dict(zip(self.indices, self.pauli_terms))
