"""
Audio sources, that are the source from
where we will obtain the data to offer
as audio in our editor.

These sources will be used by other
classes to access to the frames but 
improve the functionality and simplify
it.
"""
from yta_video_pyav.editor.sources.abstract import _AudioSource
from yta_video_pyav.reader import AudioReader
from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union

import numpy as np


class AudioFileSource(_AudioSource):
    """
    Class to represent an audio, read from an
    audio file, as an audio media source.
    """

    @property
    def copy(
        self
    ) -> 'AudioFileSource':
        """
        Get a copy of this instance.
        """
        return AudioFileSource(self.filename)

    @property
    def duration(
        self
    ) -> Fraction:
        """
        The duration of the audio.
        """
        return self.reader.audio_duration
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The frames per second of the audio.
        """
        return self.reader.audio_fps
    
    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return self.reader.audio_time_base
    
    def __init__(
        self,
        filename: str,
    ):
        self.filename: str = filename
        """
        The filename of the original audio.
        """
        self.reader: AudioReader = AudioReader(self.filename)
        """
        The pyav audio reader.
        """

    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames for a 
        given video 't' time moment, using the
        audio cache system.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).
        """
        for frame in self.reader.get_audio_frames_at_t(t, video_fps):
            yield frame

# TODO: This 'AudioNumpySource' class is
# very experimental, it needs refactor
# and I don't know if we will use it...
class AudioNumpySource(_AudioSource):
    """
    Class to represent an audio, made from a
    numpy array, as an audio media source.

    This source is static. The same audio
    frame will be returned always.
    """

    @property
    def copy(
        self
    ) -> 'AudioNumpySource':
        """
        Get a copy of this instance.
        """
        return AudioNumpySource(self._array)

    @property
    def duration(
        self
    ):
        """
        The duration of the source.
        """
        # TODO: Should I return something like 999 (?)
        return None

    # TODO: Put some information about the
    # shape we need to pass, and also create
    # a 'duration' property
    @property
    def frame(
        self
    ) -> AudioFrame:
        """
        The frame that must be played.
        """
        # TODO: What 'format' do we use? I think we
        # need to inspect the array to auto detect
        # it

        # return {
        #     's16': np.int16,
        #     'flt': np.float32,
        #     'fltp': np.float32
        # }.get(audio_format, None)
    
        # By now I'm forcing to this
        return AudioFrame.from_ndarray(
            array = self._array,
            format = 'fltp',
            layout = 'stereo'
        )

    def __init__(
        self,
        array: np.ndarray,
        # TODO: I think I need more information
        # to know how to read it
        # sample_rate (?)
    ):
        self._array: np.ndarray = array
        """
        The array of information that will be
        used to make the frame that will be
        played its whole duration.
        """
        # TODO: We should autodetect format,
        # layout and 'duration' and 'sample_rate'
        # that we will call 'audio_fps' through
        # a property

    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames for a 
        given video 't' time moment.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).

        As this is an audio from a static numpy
        array, the duration must fit 1/video_fps.
        """
        # TODO: We need to concatenate the audio
        # to make it fit the 1/video_fps duration
        # or maybe this class is unnecessary...
        yield self.frame