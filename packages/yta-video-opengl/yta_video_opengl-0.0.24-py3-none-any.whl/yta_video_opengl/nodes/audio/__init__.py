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
from yta_video_opengl.nodes import TimedNode
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
        input: Union['AudioFrame', 'np.ndarray'],
        t: float
    ) -> Union['AudioFrame', 'np.ndarray']:
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
        input: Union['AudioFrame', 'np.ndarray'],
        t: float
    ) -> Union['AudioFrame', 'np.ndarray']:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        # if PythonValidator.is_instance_of(input, 'AudioFrame'):
        #     input = input.to_ndarray().astype(np.float32)

        # TODO: I think we should receive only 
        # numpy arrays and the AudioFrame should
        # be handled outside, but I'm not sure

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

        # new_frame = AudioFrame.from_ndarray(
        #     samples,
        #     format = input.format.name,
        #     layout = input.layout.name
        # )
        # new_frame.sample_rate = input.sample_rate
        # new_frame.pts = input.pts
        # new_frame.time_base = input.time_base

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
        input: Union['AudioFrame', 'np.ndarray'],
        t: float
    ) -> Union['AudioFrame', 'np.ndarray']:
        """
        Process the provided audio 'input' that
        is played on the given 't' time moment.
        """
        # TODO: I think we should receive only 
        # numpy arrays and the AudioFrame should
        # be handled outside, but I'm not sure

        n_samples = input.shape[0]
        t = np.arange(n_samples) / self.rate

        # LFO sinusoidal que controla el retardo
        delay = (self.depth / 1000.0) * self.rate * (0.5 * (1 + np.sin(2 * np.pi * self.frequency * t)))
        delay = delay.astype(np.int32)

        output = np.zeros_like(input, dtype=np.float32)

        for i in range(n_samples):
            d = delay[i]
            if i - d >= 0:
                output[i] = 0.7 * input[i] + 0.7 * input[i - d]
            else:
                output[i] = input[i]

        return output

# TODO: Remove this below
"""
Here you have an example. The 'private'
node class is the modifier, that we don't
want to expose, and the 'public' class is
the one that inherits from TimedNode and
wraps the 'private' class to build the
functionality.
"""
# class VolumeAudioNode(TimedNode):
#     """
#     TimedNode to set the audio volume of a video
#     in a specific frame.
#     """

#     def __init__(
#         self,
#         factor_fn,
#         start: float = 0.0,
#         end: Union[float, None] = None
#     ):
#         super().__init__(
#             node = _SetVolumeAudioNode(factor_fn),
#             start = start,
#             end = end
#         )

# class _SetVolumeAudioNode(AudioNode):
#     """
#     Audio node to change the volume of an
#     audio frame.
#     """

#     def __init__(
#         self,
#         factor_fn
#     ):
#         """
#         factor_fn: function (t, index) -> factor volumen
#         """
#         self.factor_fn = factor_fn

#     def process(
#         self,
#         frame: av.AudioFrame,
#         t: float,
#     ) -> av.AudioFrame:
#         # TODO: Why index (?) Maybe 'total_frames'
#         factor = self.factor_fn(t, 0)

#         samples = frame.to_ndarray().astype(np.float32)
#         samples *= factor

#         # Determine dtype according to format
#         samples = (
#             samples.astype(np.int16)
#             # 'fltp', 's16', 's16p'
#             if 's16' in frame.format.name else
#             samples.astype(np.float32)
#         )

#         new_frame = av.AudioFrame.from_ndarray(
#             samples,
#             format = frame.format.name,
#             layout = frame.layout.name
#         )
#         new_frame.sample_rate = frame.sample_rate
#         new_frame.pts = frame.pts
#         new_frame.time_base = frame.time_base

#         return new_frame