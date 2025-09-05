from yta_video_pyav.reader import VideoReader
from yta_video_pyav.writer import VideoWriter
from yta_video_pyav.decorators import with_adjusted_t
from yta_video_pyav.utils import apply_video_effects_to_frame_at_t, apply_audio_effects_to_frame_at_t
from yta_video_opengl.effects import EffectsStack
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union


# TODO: Where can I obtain this dynamically (?)
PIXEL_FORMAT = 'yuv420p'

# TODO: Maybe create a _Media(ABC) to put
# some code shared with the Audio class
class Video:
    """
    Class to wrap the functionality related to
    handling and modifying a video.
    """

    @property
    def ticks_per_frame(
        self
    ) -> int:
        """
        The number of ticks per video frame. A
        tick is the minimum amount of time and
        is the way 'pts' is measured, in ticks.

        This means that the 'pts' value will
        be increased this amount from one video
        frame to the next one.

        How we obtain it:
        - `(1 / fps) / time_base`
        """
        return self.reader.ticks_per_frame
    
    @property
    def duration(
        self
    ) -> Fraction:
        """
        The duration of the video.
        """
        return self.end - self.start
    
    @property
    def number_of_frames(
        self
    ) -> Union[int, None]:
        """
        The number of frames of the video.
        """
        return self.reader.number_of_frames
    
    @property
    def fps(
        self
    ) -> Union[Fraction, None]:
        """
        The frames per second of the video.
        """
        return self.reader.fps
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The frames per second of the audio.
        """
        return self.reader.audio_fps

    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video frames expressed 
        like (width, height).
        """
        return self.reader.size
    
    @property
    def width(
        self
    ) -> int:
        """
        The width of the video frames in pixels.
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The height of the video frames in pixels.
        """
        return self.size[1]
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the video.
        """
        return self.reader.time_base
    
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
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ):
        self.filename: str = filename
        """
        The filename of the original video.
        """
        # TODO: Detect the 'pixel_format' from the
        # extension (?)
        self.reader: VideoReader = VideoReader(self.filename)
        """
        The pyav video reader.
        """
        self.start: Fraction = Fraction(start)
        """
        The time moment 't' in which the video
        should start.
        """
        self.end: Union[Fraction, None] = Fraction(
            # TODO: Is this 'end' ok (?)
            self.reader.duration
            if end is None else
            end
        )
        """
        The time moment 't' in which the video
        should end.
        """
        self._effects: EffectsStack = EffectsStack()
        """
        The effects we want to apply on the
        video.
        """

        if (
            self.start >= self.reader.duration and
            self.end >= self.reader.duration
        ):
            raise Exception(f'The provided "start" and "end" are invalid values considering the real video duration of {str(float(self.reader.duration))}s')
        
        if self.end <= self.start:
            raise Exception('The "end" value cannot be equal or smaller than the "start" value.')
        
        self.end = (
            self.reader.duration
            if self.end > self.reader.duration else
            self.end
        )

    @with_adjusted_t
    def get_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment, using the video cache system.
        """
        
        print(f'Getting frame from {str(float(t + self.start))} that is actually {str(float(t))}')
        return apply_video_effects_to_frame_at_t(
            effects_stack = self._effects,
            frame = self.reader.get_frame(t),
            t = t
        )
        #return self.reader.video_cache.get_frame(self._get_t(t))

    @with_adjusted_t
    def get_audio_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> 'AudioFrame':
        """
        Get the audio frame with the given 't' time
        moment, using the audio cache system. This
        method is useful when we need to combine 
        many different frames so we can obtain them
        one by one.

        TODO: Is this actually necessary (?)
        """
        return apply_audio_effects_to_frame_at_t(
            effects_stack = self._effects,
            frame = self.reader.get_audio_frame_from_t(t),
            t = t
        )
    
    @with_adjusted_t
    def get_audio_frames_from_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction, None] = None
    ):
        """
        Get the sequence of audio frames for the 
        given video 't' time moment, using the
        audio cache system.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).
        """
        video_fps = (
            self.fps
            if video_fps is None else
            video_fps
        )

        print(f'Getting audio frames from {str(float(t + self.start))} that is actually {str(float(t))}')
        for frame in self.reader.get_audio_frames_from_t(t, video_fps):
            yield apply_audio_effects_to_frame_at_t(
                effects_stack = self._effects,
                frame = frame,
                t = t
            )

    def add_effect(
        self,
        effect: 'TimedNode'
    ) -> 'Video':
        """
        Add the provided 'effect' to the video.
        """
        ParameterValidator.validate_mandatory_instance_of('effect', effect, 'TimedNode')

        self._effects.add_effect(effect)
        
        return self

    def save_as(
        self,
        filename: str
    ) -> 'Video':
        """
        Save the video locally as the given 'filename'.

        TODO: By now we are doing tests inside so the
        functionality is a manual test. Use it 
        carefully.
        """
        writer = VideoWriter(filename)
        writer.set_video_stream_from_template(self.reader.video_stream)
        writer.set_audio_stream_from_template(self.reader.audio_stream)

        from yta_video_opengl.nodes.audio import VolumeAudioNode
        # Audio from 0 to 1
        # TODO: This effect 'fn' is shitty
        def fade_in_fn(t, index, start=0.5, end=1.0):
            if t < start or t > end:
                # fuera de la franja: no tocar nada → volumen original (1.0)
                progress = 1.0
            else:
                # dentro de la franja: interpolar linealmente entre 0 → 1
                progress = (t - start) / (end - start)

            return progress

        #fade_in = SetVolumeAudioNode(lambda t, i: min(1, t / self.duration))
        fade_in = VolumeAudioNode(lambda t, i: fade_in_fn(t, i, 0.5, 1.0))

        for frame, t, index in self.frames:
            if PythonValidator.is_instance_of(frame, VideoFrame):
                print(f'Saving video frame {str(index)}, with t = {str(t)}')

                # TODO: Process any video frame change

                writer.mux_video_frame(
                    frame = frame
                )
            else:
                print(f'Saving audio frame {str(index)} ({str(round(float(t * self.reader.fps), 2))}), with t = {str(t)}')

                # TODO: Process any audio frame change
                # Test setting audio
                frame = fade_in.process(frame, t)

                writer.mux_audio_frame(
                    frame = frame
                )

        # Flush the remaining frames to write
        writer.mux_audio_frame(None)
        writer.mux_video_frame(None)

        # TODO: Maybe move this to the '__del__' (?)
        writer.output.close()
        self.reader.container.close()