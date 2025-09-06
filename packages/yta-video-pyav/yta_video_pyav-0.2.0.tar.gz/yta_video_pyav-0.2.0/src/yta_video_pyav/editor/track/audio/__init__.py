"""
The audio track module.
"""
from yta_video_pyav.editor.track.parts.audio import _AudioPart
from yta_video_pyav.editor.track.media.audio import AudioOnTrack
from yta_video_pyav.editor.track.abstract import _TrackWithAudio


class AudioTrack(_TrackWithAudio):
    """
    Class to represent a track in which we place
    audios to build a video project.
    """

    def __init__(
        self,
        index: int,
        fps: float,
        audio_fps: float,
        # TODO: Where does it come from (?)
        audio_samples_per_frame: int,
        audio_layout: str = 'stereo',
        audio_format: str = 'fltp'
    ):
        _TrackWithAudio.__init__(
            index = index,
            fps = fps,
            audio_fps = audio_fps,
            audio_samples_per_frame = audio_samples_per_frame,
            audio_layout = audio_layout,
            audio_format = audio_format
        )

    def _make_part(
        self,
        **kwargs
    ):
        return _AudioPart(**kwargs)
    
    def _make_media_on_track(
        self,
        **kwargs
    ):
        return AudioOnTrack(**kwargs)