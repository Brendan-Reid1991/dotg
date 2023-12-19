"""Stim assest package. Pythonic objectst that are wrapped around stim commands."""
from dotg.utilities.stim_assets._stim_decorators import StimDecorators
from dotg.utilities.stim_assets._stim_gates import (
    MeasureAndReset,
    MeasurementGates,
    OneQubitGates,
    ResetGates,
    TwoQubitGates,
)
from dotg.utilities.stim_assets._stim_noise_channels import (
    OneQubitNoiseChannels,
    TwoQubitNoiseChannels,
)
from typing import Union

StimGate = Union[
    OneQubitGates, TwoQubitGates, MeasurementGates, ResetGates, MeasureAndReset
]

StimNoise = Union[OneQubitNoiseChannels, TwoQubitNoiseChannels]
