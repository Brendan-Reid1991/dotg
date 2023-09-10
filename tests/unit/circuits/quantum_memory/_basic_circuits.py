from dotg.circuits.quantum_memory import color_code, rotated_surface_code
from dotg.noise import DepolarizingNoise, NoiseModel


class BasicCircuits:
    class GraphLike:
        NOISELESS_CIRCUIT = rotated_surface_code(distance=2, rounds=1)

        _noise_model = DepolarizingNoise(physical_error=1e-2)
        NOISY_CIRCUIT = _noise_model.permute_circuit(NOISELESS_CIRCUIT)

        _measurement_noise_only = NoiseModel(measurement_noise=1e-2)
        MEASUREMENT_NOISE_ONLY_CIRCUIT = _measurement_noise_only.permute_circuit(
            NOISELESS_CIRCUIT
        )

    class HypergraphLike:
        NOISELESS_CIRCUIT = color_code(distance=5, rounds=3)

        _noise_model = DepolarizingNoise(physical_error=1e-2)
        NOISY_CIRCUIT = _noise_model.permute_circuit(NOISELESS_CIRCUIT)

        _measurement_noise_only = NoiseModel(measurement_noise=1e-2)
        MEASUREMENT_NOISE_ONLY_CIRCUIT = _measurement_noise_only.permute_circuit(
            NOISELESS_CIRCUIT
        )
