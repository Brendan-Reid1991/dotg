"""A lookup table decoder."""

import random
from collections import defaultdict
import pickle as pkl
import stim
from numpy.typing import NDArray
import os
from warnings import warn

from dotg.decoders._decoder_base_class import Decoder


class LookupTable(Decoder):
    """A lookup table decoder. A rudimentary decoder, effective only for
    small circuits. Useful for a small code that does not permit a graph-like decoder.

    Functions by sampling the detector space of the input circuit, and counting the
    instances of each detector signature where the observable(s) is (are) flipped.
    The corresponding probability is then returned given an input syndrome.

    Lookup decoders are saved locally, and can be loaded into memory if they are
    pre-generated.

    Parameters
    ----------
    circuit: stim.Circuit
        A noisy stim circuit.
    name: str
        The name to give the lookup table, once saved.
    sample_size: float | int, optional
        The sample to take from the detector space to generate failure probabilities.
        By default 1_000_000.
    overwrite_table: bool, optional
        Whether or not to overwrite a previously saved table under the same name.
    Raises
    ------
    NotImplementedError
        If the sample size covers less than 5% of the search space.
    """

    DEFAULT_PATHWAY = os.getcwd() + "/.lookuptable_cache"

    def __init__(
        self,
        circuit: stim.Circuit,
        name: str,
        sample_size: float | int = 1e6,
        overwrite_table: bool = False,
    ) -> None:
        self.circuit = circuit
        self.num_observables = self.circuit.num_observables
        self.name = name
        self.sample_size = int(sample_size)
        self.overwrite_table = overwrite_table

        if self.sample_size / 2**self.circuit.num_detectors < 5e-2:
            warn(
                message="""!!!!!!!!!!!!!!!
                Your sample size covers less than 5% of the detector space.
                Your circuit may be intractable for a lookup table decoder to 
                perform reasonably.""",
                category=RuntimeWarning,
            )

        if not os.path.exists(self.DEFAULT_PATHWAY):
            os.mkdir(self.DEFAULT_PATHWAY)

        self._detector_sampler = self.circuit.compile_detector_sampler()

        self.observable_flipped_probability = self.get()

    def cast_detector_array_to_bitstring(self, detector_array: NDArray) -> str:
        """Cast a detector array to a bit string.

        i.e.
        >>> cast_detector_array_to_bitstring([True, True, True, False])
        '1110'

        Parameters
        ----------
        detector_array : NDArray

        Returns
        -------
        str
            A bit string representing the input array.
        """
        return "".join(list(map(lambda x: str(int(x)), detector_array)))

    def _generate_table(self) -> defaultdict[str, float | int]:
        """Generate a lookup table for this experiment.

        We sample from the detector space, and count the frequency of each detector
        and how often the underlying error pattern flips the logical operator.

        Returns
        -------
        defaultdict[str, float | int]
            A dictionary of detectors as bit strings, and their probability of causing
            a logical error.
        """

        detectors, observables = self._detector_sampler.sample(
            int(self.sample_size), separate_observables=True
        )
        detector_frequency: defaultdict = defaultdict(list)
        for idx, det in enumerate(detectors):
            detector_frequency[self.cast_detector_array_to_bitstring(det)].append(idx)
        return defaultdict(
            int,
            {
                sig: sum(observables[freqs][:, 0]) / len(freqs)
                for sig, freqs in detector_frequency.items()
            },
        )

    def get(self) -> defaultdict[str, float | int]:
        """Get the lookup table as a defualt dictionary object.

        Keys are detector signatures as bit strings, and values are the
        probability that detector caused a logical flip.

        If a lookup table under the same name is already saved, it is
        loaded into memory.

        Returns
        -------
        defaultdict[int, str, float | int]
        """
        filename = f"{self.DEFAULT_PATHWAY}/{self.name}.pkl"
        if os.path.exists(filename) and not self.overwrite_table:
            with open(filename, "rb+") as _f:
                _table, _circuit, _sample_size = pkl.load(_f)
                if any([_circuit != self.circuit, _sample_size != self.sample_size]):
                    raise ValueError(
                        f"""Previously saved LUT {self.name} has sample size 
                        {_sample_size}, and potentially a different circuit."""
                    )
                return defaultdict(int, dict(_table))

        lookup = self._generate_table()
        with open(filename, "wb+") as _f:
            pkl.dump((lookup, self.circuit, self.sample_size), _f)
        return lookup

    def decode_syndrome(self, syndrome: NDArray) -> None:
        raise NotImplementedError(
            """Decoding individual syndromes is not implemented
            for LUT decoders. This is because the measurement space
            is much larger than the detector space, and takes 
            longer to sample from. 
            For now, LUT decoders can only provide logical flip 
            probabilities given a detector signature,
            via `get_logical_flip_probability`."""
        )

    def get_logical_flip_probability(self, syndrome: NDArray) -> float:
        """Get the probability of a logical error given an input syndrome.

        Parameters
        ----------
        syndrome : NDArray
            An input syndrome.

        Returns
        -------
        float
            Probability that this syndrome caused a logical error.
        """
        return self.observable_flipped_probability[
            self.cast_detector_array_to_bitstring(syndrome)
        ]

    def logical_error(self, num_shots: int | float) -> float:
        """Compute the logical error for this circuit.

        Parameters
        ----------
        num_shots : int | float
            Number of shots to take.

        Returns
        -------
        float
            Logical error rate.
        """
        detector_sampler = self.circuit.compile_detector_sampler()
        detectors, observables = detector_sampler.sample(
            shots=int(num_shots), separate_observables=True
        )
        failure_rate: int = 0
        for det, ob in zip(detectors, observables):
            prob = self.observable_flipped_probability[
                self.cast_detector_array_to_bitstring(det)
            ]
            if (random.random() < prob and not ob[0]) or (
                random.random() > prob and ob[0]
            ):
                failure_rate += 1

        return failure_rate / num_shots
