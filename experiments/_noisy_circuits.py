from dotg.circuits import rotated_surface_code
from dotg.noise import DepolarizingNoise

if __name__ == "__main__":
    noise_model = DepolarizingNoise(physical_error=1e-3)
    circuit = rotated_surface_code(distance=2)
    print(circuit)
    circuit = noise_model.permute_circuit(circuit)
    print(circuit)
