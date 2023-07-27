"""Module to define a base class for all stim enums."""
from typing import List
from enum import Enum


class StimOperations(Enum):
    """Top level enum for all stim operations.
    """
    @classmethod
    def members(cls) -> List[str]:
        """classmethod to get all members of an Enum returned as a list.

        Returns
        -------
        List[str]
            The values of the enum returned as a list.
        """
        return list(map(lambda member: member.value, cls))
