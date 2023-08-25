"""Module to define a base class for all stim enums."""
from enum import Enum
from typing import List


class StimOperations(Enum):
    """Top level enum for all stim operations."""

    @classmethod
    def members(cls) -> List[str]:
        """classmethod to get all members of an Enum returned as a list.

        Returns
        -------
        List[str]
            The values of the enum returned as a list.
        """
        return list(map(lambda member: member.value, cls))
