"""This module provides a function to divide a stim circuit into timelike layers."""
from typing import List

import stim

from dotg.utilities.stim_assets import StimDecorators


def get_circuit_layers(circuit: stim.Circuit) -> List[stim.Circuit]:
    """Divide a stim circuit into a list of subcircuits, splitting them by the TICK stim
    decorators, such that each subcircuit represents one timestep.

    Parameters
    ----------
    circuit : stim.Circuit
        Stim circuit to divide.

    Returns
    -------
    List[stim.Circuit]
        List of stim circuits, where each element represents one timestep of the circuit.
    """
    layers = [
        idx + 1 for idx, instr in enumerate(circuit) if instr.name == StimDecorators.TICK
    ]
    circuit_by_layers = [
        (list(circuit) + [""])[slice(ix, iy)]
        for ix, iy in zip([0] + layers, layers + [-1])
    ]
    sub_circuits = []
    for layer in circuit_by_layers:
        new_circ = stim.Circuit()
        for instr in layer:
            new_circ.append(name=instr)
        sub_circuits.append(new_circ)

    return sub_circuits
