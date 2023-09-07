"""Module to define a base class for all stim enums."""
from enum import StrEnum
from typing import List


class StimOperations(StrEnum):
    """Top level enum for all stim operations."""

    @classmethod
    def members(cls) -> List[str]:
        """classmethod to get all members of an Enum returned as a list.

        Returns
        -------
        List[str]
            The values of the enum returned as a list.
        """
        return [member.value for member in cls]
