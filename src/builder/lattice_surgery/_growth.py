"""An experimental file to grow a logical qubit."""

from builder.lattice_surgery._experiment import LatticeSurgeryExperiment
from builder.utilities.grids._square_grid import SquareGrid

class Growth(LatticeSurgeryExperiment):
    def __init__(self, initial_distances: tuple[int, int], final_distances: tuple[int, int]):

        