"""This module provides an abstract base class for Belief Propagation based decoders."""
from abc import ABC
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional

import numpy as np
import stim
from ldpc import bp_decoder, bposd_decoder
from numpy.typing import NDArray

from dotg.decoders._decoder_base_class import Decoder
from dotg.utilities import CircuitUnderstander


class MessageUpdates(IntEnum):
    """An enum for accessing min-sum and prod-sum updates in belief propagation.

    Options:
        - PROD_SUM = 0
        - MIN_SUM = 1
    """

    PROD_SUM: int = 0
    MIN_SUM: int = 1


class OSDMethods(IntEnum):
    """An enum for accessing OSD methods in BPOSD. These inform the OSD order parameter,
    however it can be overwritten when using the exhaustive method.

    Options:
        - ZERO = 0
        - EXHAUSTIVE = 1
        - COMBINATION_SWEEP = 2
    """

    ZERO = 0
    EXHAUSTIVE = 1
    COMBINATION_SWEEP = 2


@dataclass
class LDPCDecoderOptions:
    """Dataclass that collates all options for belief propagation (BP) and BPOSD
    decoders. The only required input is the maximum number of iterations.

    Parameters
    ----------
    max_iterations : int
        Maximum number of message passing stages to execute before terminating the BP
        algorithm.
    message_updates : MessageUpdates, optional
        Which message updating schema to use, by default None. If None, will revert to
        product sum updates.
    min_sum_scaling_factor : float, optional
        Sets the scaling factor for min-sum updates. See arXiv:2005.07016 for more
        details.
    osd_method : OSDMethods, optional
        Which OSD method to use, by default None. Must be explicitly set if using BPOSD.
    osd_order : int, optional
        Order parameter for OSD, by default None. If osd_method is given, this value can
        be inferred:
            osd_method = OSDMethods.ZERO --> osd_order = 0;\n
            osd_method = OSDMethods.EXHAUSTIVE --> osd_order = 10;\n
            osd_method = OSDMethods.COMBINATION_SWEEP --> osd_order = -1;\n
        However, for OSDMethods.EXHAUSTIVE the value can be overwritten, but will raise a
        warning above 15.


    Raises
    ------
    ValueError
        If max_iterations is not positive and non-zero, or it is not an int.
    ValueError
        If message_updates is not valid.
    ValueError
        If osd_method is not valid.
    ValueError
        If osd_method has not been set but osd_order has.
    """

    max_iterations: int
    message_updates: Optional[MessageUpdates] = None
    min_sum_scaling_factor: Optional[float] = None
    osd_method: Optional[OSDMethods] = None
    osd_order: Optional[int] = None

    def __post_init__(self):
        if self.max_iterations <= 0 or not isinstance(self.max_iterations, int):
            raise ValueError(
                "Max iterations needs to be a positive, non-zero integer. "
                f"Received: {self.max_iterations}"
                ""
            )
        self.message_updates = self.message_updates or MessageUpdates.PROD_SUM

        if self.message_updates not in [0, 1]:
            raise ValueError("Invalid message updating scheme.")

        if self.message_updates == 1:
            self.min_sum_scaling_factor = self.min_sum_scaling_factor or 1

        if self.osd_method not in [0, 1, 2, None]:
            raise ValueError("Invalid OSD method.")

        if self.osd_order and self.osd_method is None:
            raise ValueError("OSD Method configuration must be given.")

        if self.osd_method == 0:
            self.osd_order = 0

        if self.osd_method == 1:
            self.osd_order = self.osd_order or 10

        if self.osd_method == 2:
            self.osd_order = -1


class LDPCBeliefPropagationDecoder(Decoder, ABC):
    """A base class for decoders that inherit from the bp_decoder object in the LDPC
    package.

    Parameters
    ----------
    circuit : stim.Circuit
        Stim circuit that defines our experiment.
    decoder_options : LDPCDecoderOptions, optional
        Which decoder options to pass, by default:
            LDPCDecoderOptions(
                max_iterations=1,
                message_updates=MessageUpdates.PROD_SUM
            )
    """

    def __init__(
        self,
        circuit: stim.Circuit,
        decoder_options: LDPCDecoderOptions = LDPCDecoderOptions(
            max_iterations=1, message_updates=MessageUpdates.PROD_SUM
        ),
    ):
        super().__init__(circuit=circuit)
        self.decoder_options = decoder_options

        self._understander = CircuitUnderstander(circuit=circuit)

        self.parity_check = np.asarray(self._understander.parity_check)
        self.logical_check = np.asarray(self._understander.logical_check)
        self.error_probabilities = np.asarray(self._understander.error_probabilities)

        self.decoder = self.decoder_options

    @property
    def decoder(self) -> bp_decoder:
        """Return the raw decoder object from the LDPC package.

        Returns
        -------
        bp_decoder
            Decoder object from the LDPC package.
        """
        return self._decoder

    @decoder.setter
    def decoder(self, decoder_options: LDPCDecoderOptions):
        """Setter for the decoder property.

        Parameters
        ----------
        decoder_options : LDPCDecoderOptions
            Decoder options. Determins which decoder object is used.
        """
        input_vector_type = 0
        if decoder_options.osd_method:
            # BPOSD Branch
            if decoder_options.message_updates == 0:
                self._decoder = bposd_decoder(
                    parity_check_matrix=self.parity_check,
                    max_iter=decoder_options.max_iterations,
                    channel_probs=self.error_probabilities,
                    input_vector_type=input_vector_type,
                    ###################################
                    bp_method=decoder_options.message_updates,
                    osd_method=decoder_options.osd_method,
                    osd_order=decoder_options.osd_order,
                )
            else:
                self._decoder = bposd_decoder(
                    parity_check_matrix=self.parity_check,
                    max_iter=decoder_options.max_iterations,
                    channel_probs=self.error_probabilities,
                    input_vector_type=input_vector_type,
                    ###################################
                    bp_method=decoder_options.message_updates,
                    ms_scaling_factor=decoder_options.min_sum_scaling_factor,
                    osd_method=decoder_options.osd_method,
                    osd_order=decoder_options.osd_order,
                )
        else:
            # BP Branch
            if decoder_options.message_updates == 0:
                self._decoder = bp_decoder(
                    parity_check_matrix=self.parity_check,
                    max_iter=decoder_options.max_iterations,
                    channel_probs=self.error_probabilities,
                    input_vector_type=input_vector_type,
                    ###################################
                    bp_method=decoder_options.message_updates,
                )
            else:
                self._decoder = bp_decoder(
                    parity_check_matrix=self.parity_check,
                    max_iter=decoder_options.max_iterations,
                    channel_probs=self.error_probabilities,
                    input_vector_type=input_vector_type,
                    ###################################
                    bp_method=decoder_options.message_updates,
                    ms_scaling_factor=decoder_options.min_sum_scaling_factor,
                )

    def is_logical_failure(
        self, error_pattern: List[int] | NDArray, logical: bool
    ) -> bool:
        """Given a specific logical that relates to a physical error event, check if the
        error pattern triggers the same logical pattern. This method is used to check for
        logical failures in decoding, i.e. if the input logical is 1 but the error
        pattern returns a logical pattern 0, a logical observable has been flipped and
        we have not detected it.

        Parameters
        ----------
        error_pattern : List[int]
            An error pattern to check.
        logical : List[int]
            Logical error pattern to compare to.

        Returns
        -------
        bool
            Whether or not the input error pattern results in the same logical pattern as logical.
        """
        if [
            sum(x * y for x, y in zip(log, error_pattern)) % 2
            for log in self.logical_check
        ] != logical:
            return True
        return False

    @property
    def num_iterations(self) -> int:
        """Return the number of iterations it took for the BP algorithm to terminate.

        Returns
        -------
        int
        """
        return self._decoder.iter

    @property
    def posterior_log_probability_odds(self) -> List[float]:
        """Return the list of posterior log probability odds after the BP algorithm
        has ran. Returns all 0 if no decoding has taken place.

        Returns
        -------
        List[float]
            Posterior log probability odds.
        """
        return self._decoder.log_prob_ratios

    @property
    def posterior_probability_odds(self) -> List[float]:
        """Return the list of posterior probability odds after the BP algorithm
        has ran. Returns all 1 if no decoding has taken place.

        Returns
        -------
        List[float]
            Posterior probability odds.
        """
        return list(1 / np.exp(self.posterior_log_probability_odds))

    @property
    def posterior_probabilities(self) -> List[float]:
        """Return the list of posterior probabilities after the BP algorithm
        has ran. Returns all 0.5 if no decoding has taken place.

        Returns
        -------
        List[float]
            Posterior probabilities.
        """
        posterior_odds = self.posterior_probability_odds

        return [x / (1 + x) for x in posterior_odds]

    @property
    def converged(self) -> bool:
        """Return whether or not the BP algorithm converged.

        Returns
        -------
        bool
        """
        return bool(self._decoder.converge)
