from typing import List, Type

import pytest

from dotg.utilities._stim_operations import StimOperations


class BaseTestStimOperations:
    ENUM: Type[StimOperations] = StimOperations
    CURRENT_MEMBERS: List[str] = ["..."]

    @pytest.fixture(scope="class")
    def _self(self):
        return self.ENUM

    def test_all_names_and_values_match(self, _self):
        assert all(x.name == x.value for x in _self)

    def test_current_members_match_input(self, _self):
        assert _self.members() == self.CURRENT_MEMBERS
