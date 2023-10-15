from dotg.decoders import BPOSD, LDPCDecoderOptions, OSDMethods
from dotg.decoders._manager import DecoderManager
from dotg.circuits import SurfaceCode
from dotg.noise import DepolarizingNoise

code = SurfaceCode.Rotated(distance=5)
circuit = DepolarizingNoise(physical_error=1e-3).permute_circuit(code.memory)

decoder = BPOSD(
    circuit=circuit,
    decoder_options=LDPCDecoderOptions(
        max_iterations=5, osd_method=OSDMethods.EXHAUSTIVE
    ),
)

manager = DecoderManager(decoder=decoder)

print(manager.run(num_shots=int(1e4)))
