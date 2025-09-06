from quicktions import Fraction
from abc import ABC, abstractmethod
from typing import Union


class _VideoSource(ABC):
    """
    Abstract class that is a media source
    containing video information.
    """

    @property
    @abstractmethod
    def copy(
        self
    ):
        """
        Get a copy of this video source instance.
        """
        pass

    @property
    @abstractmethod
    def duration(
        self
    ):
        """
        The duration of the source.
        """
        pass

    def __init__(
        self
    ):
        pass

    @abstractmethod
    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
        # TODO: Return 'VideoFrame' or 'numpy' (?)
    ):
        """
        Get the video frame that must be displayed
        at the 't' time moment.
        """
        pass

    @abstractmethod
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction]
        # TODO: Return 'VideoFrame' or 'numpy' (?)
    ):
        """
        Get the audio frames that must be played
        during the 't' time moment of a video.
        """
        pass

    # TODO: audio frames t (?)
        
class _AudioSource(ABC):
    """
    Abstract class that is a media source
    containing audio information.
    """

    @property
    @abstractmethod
    def copy(
        self
    ):
        """
        Get a copy of this video source instance.
        """
        pass

    @property
    @abstractmethod
    def duration(
        self
    ):
        """
        The duration of the source.
        """
        pass

    def __init__(
        self
    ):
        pass

    @abstractmethod
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction]
        # TODO: Return 'VideoFrame' or 'numpy' (?)
    ):
        """
        Get the audio frames that must be played
        during the 't' time moment of a video.
        """
        pass

