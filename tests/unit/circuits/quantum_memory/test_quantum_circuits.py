"""Test file for dotg.circuits._quantum_circuits.py"""
from __future__ import annotations

import pytest
import stim

from dotg.circuits.quantum_memory import (
    color_code,
    rotated_surface_code,
    unrotated_surface_code,
)

# pylint: disable=no-member,missing-function-docstring


@pytest.mark.parametrize("distance", [3, 5, 7, 9])
@pytest.mark.parametrize(
    "circuit_function", [rotated_surface_code, unrotated_surface_code, color_code]
)
def test_return_type_is_always_stim_circuit(circuit_function, distance):
    assert isinstance(circuit_function(distance=distance), stim.Circuit)


@pytest.mark.parametrize(
    "circuit_function", [rotated_surface_code, unrotated_surface_code]
)
def test_warning_is_raised_for_unrecognised_memory_basis(circuit_function):
    with pytest.warns():
        circuit_function(distance=5, memory_basis="l")


@pytest.mark.parametrize(
    "circuit_function", [rotated_surface_code, unrotated_surface_code, color_code]
)
def test_circuit_is_always_flattened(circuit_function):
    assert not any(
        isinstance(instruction, stim.CircuitRepeatBlock)
        for instruction in circuit_function(distance=5)
    )


@pytest.mark.parametrize(
    "circuit_function", [rotated_surface_code, unrotated_surface_code, color_code]
)
def test_increasing_rounds_increases_length_of_circuit(circuit_function):
    assert len(circuit_function(distance=3, rounds=5)) > len(
        circuit_function(distance=3, rounds=3)
    )


@pytest.mark.parametrize(
    "circuit_function", [rotated_surface_code, unrotated_surface_code]
)
def test_changing_bases_changes_gate_set(circuit_function):
    assert all(
        instr.name not in ["RX", "MX"]
        for instr in circuit_function(distance=3, rounds=1)
    )
    assert any(
        instr.name in ["RX", "MX"]
        for instr in circuit_function(distance=3, rounds=1, memory_basis="x")
    )
