"""
When working with audio frames, we don't need
to use the GPU because audios are 1D and the
information can be processed perfectly with
a library like numpy.

If we need a very intense calculation for an
audio frame (FFT, convolution, etc.) we can
use CuPy or some DPS specific libraries, but
90% is perfectly done with numpy.

If you want to modify huge amounts of audio
(some seconds at the same time), you can use
CuPy, that has the same API as numpy but
working in GPU. Doing this below most of the
changes would work:
- `import numpy as np` → `import cupy as np`
"""
from abc import abstractmethod
from typing import Union

import numpy as np


class _AudioNode:
    """
    Base audio node class to implement a
    change in an audio frame by using the
    numpy library.
    """

    @abstractmethod
    def process(
        self,
        input: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        pass

class VolumeNode(_AudioNode):
    """
    Set the volume.

    TODO: Explain properly.
    """

    def __init__(
        self,
        factor_fn
    ):
        """
        factor_fn: function (t, index) -> factor volumen
        """
        self.factor_f: callable = factor_fn

    def process(
        self,
        input: np.ndarray,
        t: float
    ) -> np.ndarray:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        factor = self.factor_fn(t, 0)

        samples = input
        samples *= factor

        # Determine dtype according to format
        # samples = (
        #     samples.astype(np.int16)
        #     # 'fltp', 's16', 's16p'
        #     if 's16' in input.format.name else
        #     samples.astype(np.float32)
        # )

        return samples
    
class ChorusNode(_AudioNode):
    """
    Apply a chorus effect, also called flanger
    effect.

    TODO: Explain properly
    """

    def __init__(
        self,
        sample_rate: int,
        depth: int = 0,
        frequency: float = 0.25
    ):
        """
        The 'sample_rate' must be the sample rate
        of the audio frame.
        """
        self.sample_rate: int = sample_rate
        self.depth: int = depth
        self.frequency: float = frequency

    def process(
        self,
        input: Union[np.ndarray],
        t: float
    ) -> np.ndarray:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        n_samples = input.shape[0]
        t = np.arange(n_samples) / self.rate

        # LFO sinusoidal que controla el retardo
        delay = (self.depth / 1000.0) * self.rate * (0.5 * (1 + np.sin(2 * np.pi * self.frequency * t)))
        delay = delay.astype(np.int32)

        output = np.zeros_like(input, dtype=np.float32)

        for i in range(n_samples):
            d = delay[i]

            output[i]= (
                0.7 * input[i] + 0.7 * input[i - d]
                if (i - d) >= 0 else
                input[i]
            )

        return output