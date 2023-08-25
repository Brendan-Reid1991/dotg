from dotg.circuits import rotated_surface_code
from dotg.noise import DepolarizingNoise, NoiseModel

NOISELESS_CIRCUIT = rotated_surface_code(distance=2, rounds=1)
_noise_model = DepolarizingNoise(physical_error=1e-2)
NOISY_CIRCUIT = _noise_model.permute_circuit(NOISELESS_CIRCUIT)

measurement_noise_only = NoiseModel(measurement_noise=1e-2)
MEASUREMENT_NOISE_ONLY_CIRCUIT = measurement_noise_only.permute_circuit(
    NOISELESS_CIRCUIT
)
