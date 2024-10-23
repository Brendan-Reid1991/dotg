import pytest

from builder.utilities import QubitCoordinate


class TestQubitCoordinate:
    @pytest.mark.parametrize("coord", [(0, 1), (1, 0), (0.5, 5.5)])
    def test_x_and_y_attrs(self, coord):
        q = QubitCoordinate(*coord)
        assert q.x == coord[0] and q.y == coord[1]

    def test_default_index_is_minus1(self):
        QubitCoordinate(0, 0).idx == -1

    def test_idx_setter(self):
        q = QubitCoordinate(0, 0)
        initial_index = q.idx
        q.idx = 400
        final_index = q.idx

        assert initial_index == -1 and final_index == 400

    def test_adder(self):
        q0 = QubitCoordinate(4, 5)
        q1 = QubitCoordinate(5, 3)
        assert QubitCoordinate(9, 8) == q0 + q1

    def test_adder_raises_error_if_obj_too_large(self):
        q0 = QubitCoordinate(0, 0)
        with pytest.raises(ValueError, match="Coordinates should all be of size 2"):
            q0 + (1, 1, 1)
