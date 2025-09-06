"""
If we have a video placed in a timeline,
starting at the t=2s and the video lasts
2 seconds, the `t` time range in which the
video is playing is `[2s, 4s]`, so here 
you have some examples with global `t` 
values:
- `t=1`, the video is not playing because
it starts at `t=2`
- `t=3`, the video is playing, it started
at `t=2` and it has been playing during 1s
- `t=5`, the video is not playing because
it started at `t=2`, lasting 2s, so it
finished at `t=4`
"""
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from quicktions import Fraction
from typing import Union
from abc import ABC


class _MediaOnTrack(ABC):
    """
    Class to be inherited by any media class
    that will be placed on a track and should
    manage this condition.
    """

    @property
    def end(
        self
    ) -> Fraction:
        """
        The end time moment 't' of the audio once
        once its been placed on the track, which
        is affected by the audio duration and its
        start time moment on the track.

        This end is different from the audio end.
        """
        return self.start + self.media.duration

    def __init__(
        self,
        media: Union['AudioFileMedia', 'VideoFileMedia', 'VideoColorMedia', 'VideoImageMedia'],
        start: Union[int, float, Fraction] = 0.0
    ):
        ParameterValidator.validate_mandatory_instance_of('media', media, ['AudioFileMedia', 'VideoFileMedia', 'VideoColorMedia', 'VideoImageMedia'])
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)

        self.media: Union['AudioFileMedia', 'VideoFileMedia', 'VideoColorMedia', 'VideoImageMedia'] = media
        """
        The media source, with all its properties,
        that is placed in the timeline.
        """
        self.start: Fraction = Fraction(start)
        """
        The time moment in which the media should
        start playing, within the timeline.

        This is the time respect to the timeline
        and its different from the media `start`
        time, which is related to the file.
        """
    
    def _get_t(
        self,
        t: Union[int, float, Fraction]
    ) -> float:
        """
        The media 't' time moment for the given
        global 't' time moment. This 't' is the one
        to use inside the media content to display
        its frame.
        """
        # TODO: Should we make sure 't' is truncated (?)
        return t - self.start

    def is_playing(
        self,
        t: Union[int, float, Fraction]
    ) -> bool:
        """
        Check if this media is playing at the general
        't' time moment, which is a global time moment
        for the whole project.
        """
        # TODO: Should we make sure 't' is truncated (?)
        return self.start <= t < self.end
    
class _MediaOnTrackWithAudio(_MediaOnTrack):
    """
    Class that implements the ability of
    getting audio frames. This class must
    be inherited by any other class that
    has this same ability.
    """

    def __init__(
        self,
        media: Union['AudioFileMedia', 'VideoFileMedia', 'VideoColorMedia', 'VideoImageMedia'],
        start: Union[int, float, Fraction] = 0.0
    ):
        super().__init__(
            media = media,
            start = start
        )

    def get_audio_frames_at(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction]
    ):
        """
        Get the audio frames that must be played at
        the 't' time moment provided, that could be
        None if the audio is not playing at that
        moment.

        This method will return None if no audio
        frames found in that 't' time moment, or an
        iterator if yes.
        """
        # TODO: Use 'T' here to be precise or the
        # argument itself must be precise (?)
        frames = (
            self.media.get_audio_frames_at_t(
                t = self._get_t(t),
                video_fps = video_fps
            )
            if self.is_playing(t) else
            []
        )

        for frame in frames:
            yield frame

class _MediaOnTrackWithVideo(_MediaOnTrack):
    """
    Class that implements the ability of
    getting video frames. This class must
    be inherited by any other class that
    has this same ability.
    """

    def __init__(
        self,
        media: Union['VideoFileMedia', 'VideoColorMedia', 'VideoImageMedia'],
        start: Union[int, float, Fraction] = 0.0
    ):
        super().__init__(
            media = media,
            start = start
        )

    def get_video_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[VideoFrame, None]:
        """
        Get the frame for the 't' time moment provided,
        that could be None if the video is not playing
        in that moment.
        """
        # TODO: Use 'T' here to be precise or the
        # argument itself must be precise (?)
        return (
            self.media.get_video_frame_at_t(
                t = self._get_t(t)
            )
            if self.is_playing(t) else
            None
        )