"""Test file for dotg.circuits._quantum_circuits.py"""
import pytest
import stim

from dotg.circuits import rotated_surface_code, unrotated_surface_code, color_code

# pylint: disable=no-member,missing-function-docstring


@pytest.mark.parametrize("distance", [3, 5, 7, 9])
@pytest.mark.parametrize(
    "circuit_function", [rotated_surface_code, unrotated_surface_code, color_code]
)
def test_return_type_is_always_stim_circuit(circuit_function, distance):
    assert isinstance(circuit_function(distance=distance), stim.Circuit)
