"""Module to define a base class for all stim enums."""

from enum import Enum, EnumMeta
from typing import Any, List


class _StimOpsMeta(EnumMeta):
    def __contains__(cls: type[Any], member: object) -> bool:
        return member in cls.__members__


class StimOperations(str, Enum, metaclass=_StimOpsMeta):
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
