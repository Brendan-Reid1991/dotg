from builder.utilities import PauliProduct

import pytest
import stim

STRINGS = ["X0", "Z0.Y1.X23", stim.PauliString("__X____Y__Z__X")]
STRING_OUTPUT = ["X0", "Z0.Y1.X23", "X2.Y7.Z10.X13"]
INDICES = [[0], [0, 1, 23], [2, 7, 10, 13]]
PAULIS = [["X"], ["Z", "Y", "X"], ["X", "Y", "Z", "X"]]
INDEX_TO_PAULI_MAP = [dict(zip(idx, pauli)) for idx, pauli in zip(INDICES, PAULIS)]


class TestPauliProduct:
    @pytest.mark.parametrize("input_string", STRINGS)
    def test_object_returned_is_PauliProduct(self, input_string):
        assert isinstance(PauliProduct(input_string), PauliProduct)

    @pytest.mark.parametrize("input_strings, indices", zip(STRINGS, INDICES))
    def test_output_indices(self, input_strings, indices):
        assert PauliProduct(input_strings).indices == indices

    @pytest.mark.parametrize("input_strings, paulis", zip(STRINGS, PAULIS))
    def test_output_paulis(self, input_strings, paulis):
        assert PauliProduct(input_strings).pauli_terms == paulis

    @pytest.mark.parametrize(
        "input_strings, index_to_pauli_map", zip(STRINGS, INDEX_TO_PAULI_MAP)
    )
    def test_output_paulis(self, input_strings, index_to_pauli_map):
        assert PauliProduct(input_strings).index_to_pauli_map == index_to_pauli_map

    @pytest.mark.parametrize("input_string, output_string", zip(STRINGS, STRING_OUTPUT))
    def test_str_and_repr_dunders(self, input_string, output_string):
        p = PauliProduct(input_string)
        assert str(p) == str(
            output_string
        ), f"""`str` output failed for input {input_string}"""
        assert (
            repr(p) == output_string
        ), f"""`repr` output failed for input {input_string}"""

    @pytest.mark.parametrize(
        "first, second, output",
        [
            list(map(PauliProduct, ["X0.Y1", "Y3.Z2", "X0.Y1.Z2.Y3"])),
            list(
                map(
                    PauliProduct, ["Z43.X45", "Z0.Z1.Z2.Z3.Z4", "Z0.Z1.Z2.Z3.Z4.Z43.X45"]
                )
            ),
            list(map(PauliProduct, ["X0.X1.X2.X3.X4.Y1", "Y3.Z2", "X0.Z1.Y2.Z3.X4"])),
        ],
    )
    def test_adding_two_pauliproducts(self, first, second, output):
        assert first + second == output

    @pytest.mark.parametrize(
        "input_string, output_string",
        [
            ["X0.Y0.X0.Z0.X0.Y0.Z1", "Y0.Z1"],
            ["Y12.X12.Y12.Z12.X4.Y4.Z5.X1", "X1.Z4.Z5.Y12"],
            ["X0.X0.X0.X0.X0.X0", ""],
        ],
    )
    def test_condensing(self, input_string, output_string):
        p = PauliProduct(input_string)
        assert p == output_string

    @pytest.mark.parametrize("invalid_input", ["XX_YY_Z", "X0Y4Y3Y1", "x0.x1.x2x3"])
    def test_error_raised_for_invalid_input(self, invalid_input):
        with pytest.raises(
            ValueError,
            match="Some entries do not follow the correct pattern for a Pauli product.",
        ):
            PauliProduct(invalid_input)

    def test_empty_string_is_returned_as_is(self):
        assert PauliProduct("") == ""

    def test_empty_string_returns_no_indices(self):
        p = PauliProduct("")
        assert not p.indices
