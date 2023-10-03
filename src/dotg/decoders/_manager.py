from typing import Callable, Optional
import multiprocessing as mp
from functools import partial


def parallelize(function: Callable):
    def decorator(instance, **kwargs):
        with mp.Pool(processes=instance.cores) as pool:
            outcome = pool.map(partial(function, **kwargs), range(instance.cores))
        return outcome

    return decorator


class Decoder:
    def __init__(self) -> None:
        pass

    def toy(self, num_shots):
        print(num_shots)
        return num_shots


class DecoderManager:
    def __init__(self, decoder: Decoder, cores: Optional[int] = None) -> None:
        self.decoder = decoder
        self.cores = cores or mp.cpu_count()

    @parallelize
    def toy(self, kwargs):
        return self.decoder.toy(**kwargs)


if __name__ == "__main__":
    manager = DecoderManager(decoder=Decoder())
    outcome = manager.toy(num_shots=1000)
    print(outcome)
