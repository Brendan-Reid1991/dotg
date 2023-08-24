"""This module provides functionality for accessing the options for decoders based on the 
BP algorithm from the LDPC package."""
from enum import IntEnum


class MessageUpdates(IntEnum):
    """An enum for accessing min-sum and prod-sum updates in belief propagation.

    Options:
        - PROD_SUM = 0
        - MIN_SUM = 1
    """

    PROD_SUM: int = 0
    MIN_SUM: int = 1
