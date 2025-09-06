from yta_video_pyav.editor.utils.frame_generator import AudioFrameGenerator
from yta_video_pyav.editor.utils.frame_wrapper import AudioFrameWrapped
from yta_video_frame_time.t_fraction import fps_to_time_base
from yta_video_opengl.effects import EffectsStack
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union


def audio_frames_and_remainder_per_video_frame(
    # TODO: Maybe force 'fps' as int (?)
    video_fps: Union[float, Fraction],
    sample_rate: int, # audio_fps
    number_of_samples_per_audio_frame: int
) -> tuple[int, int]:
    """
    Get how many full silent audio frames we
    need and the remainder for the last one
    (that could be not complete), according
    to the parameters provided.

    This method returns a tuple containing
    the number of full silent audio frames
    we need and the number of samples we need
    in the last non-full audio frame.
    """
    # Video frame duration (in seconds)
    time_base = fps_to_time_base(video_fps)
    sample_rate = Fraction(int(sample_rate), 1)

    # Example:
    # 44_100 / 60 = 735  ->  This means that we
    # will have 735 samples of sound per each
    # video frame
    # The amount of samples per frame is actually
    # the amount of samples we need, because we
    # are generating it...
    samples_per_frame = sample_rate * time_base
    # The 'nb_samples' is the amount of samples
    # we are including on each audio frame
    full_audio_frames_needed = samples_per_frame // number_of_samples_per_audio_frame
    remainder = samples_per_frame % number_of_samples_per_audio_frame
    
    return int(full_audio_frames_needed), int(remainder)

"""
These methods below are shared by the
Audio and Video class that handle and
wrap an audio or video.
"""
def apply_video_effects_to_frame_at_t(
    effects_stack: EffectsStack,
    frame: Union[VideoFrame, 'ndarray'],
    t: Union[int, float, 'Fraction']
) -> Union[VideoFrame, 'ndarray']:
    """
    Apply the video effects to the given
    'frame' on the 't' time moment provided.

    This method should be called before 
    yielding any frame.
    """
    # TODO: I think we shouldn't receive a
    # 'ndarray' here, it must be VideoFrame
    ParameterValidator.validate_mandatory_instance_of('frame', frame, [VideoFrame, 'ndarray'])

    # TODO: What about the format? 'rgb24' is
    # working but it has to be dynamic
    format = 'rgb24'

    # Need the frame as a numpy
    new_frame = (
        frame.to_ndarray(format = format)
        if PythonValidator.is_instance_of(frame, VideoFrame) else
        frame
    )

    new_frame = effects_stack.apply_video_effects_at_t(
        frame = new_frame,
        # The 't' here is the internal valid one
        t = t
    )

    # Rebuild the VideoFrame
    new_frame = VideoFrame.from_ndarray(
        # TODO: Getting this:
        #  Unexpected numpy array shape `(1080, 1920, 4)`
        # TODO: Make it work with RGBA in a near future
        array = new_frame[:, :, :3],
        #array = new_frame,
        # TODO: Getting this:
        # Conversion from numpy array with format `<av.VideoFormat yuv420p, 1920x1080>` is not yet supported
        #format = frame.format,
        format = format
    )
    new_frame.time_base = frame.time_base
    new_frame.pts = frame.pts

    return new_frame

def apply_audio_effects_to_frame_at_t(
    effects_stack: EffectsStack,
    frame: Union['AudioFrame', 'ndarray'],
    t: Union[int, float, 'Fraction']
) -> Union['AudioFrame', 'ndarray']:
    """
    Apply the audio effects to the given
    'frame' on the 't' time moment provided.

    This method should be called before 
    yielding any frame.
    """
    # TODO: I think we shouldn't receive a
    # 'ndarray' here, it must be AudioFrame
    ParameterValidator.validate_mandatory_instance_of('frame', frame, [AudioFrame, 'ndarray'])

    # Need the frame as a numpy
    new_frame = (
        frame.to_ndarray()
        if PythonValidator.is_instance_of(frame, AudioFrame) else
        frame
    )
    
    new_frame = effects_stack.apply_audio_effects_at_t(
        frame = new_frame,
        # The 't' here is the internal valid one
        t = t
    )

    # Rebuild the AudioFrame
    new_frame = AudioFrame.from_ndarray(
        array = new_frame,
        format = frame.format,
        layout = frame.layout
    )
    new_frame.sample_rate = frame.sample_rate
    new_frame.time_base = frame.time_base
    new_frame.pts = frame.pts

    return new_frame


# TODO: Is this method here ok (?)
def generate_silent_frames(
    fps: int,
    audio_fps: int,
    audio_samples_per_frame: int,
    layout: str = 'stereo',
    format: str = 'fltp'
) -> list[AudioFrameWrapped]:
    """
    Get the audio silent frames we need for
    a video with the given 'fps', 'audio_fps'
    and 'audio_samples_per_frame', using the
    also provided 'layout' and 'format' for
    the audio frames.

    This method is used when we have empty
    parts on our tracks and we need to 
    provide the frames, that are passed as
    AudioFrameWrapped instances and tagged as
    coming from empty parts.
    """
    audio_frame_generator: AudioFrameGenerator = AudioFrameGenerator()

    # Check how many full and partial silent
    # audio frames we need
    number_of_frames, number_of_remaining_samples = audio_frames_and_remainder_per_video_frame(
        video_fps = fps,
        sample_rate = audio_fps,
        number_of_samples_per_audio_frame = audio_samples_per_frame
    )

    # The complete silent frames we need
    silent_frame = audio_frame_generator.silent(
        sample_rate = audio_fps,
        layout = layout,
        number_of_samples = audio_samples_per_frame,
        format = format,
        pts = None,
        time_base = None
    )
    
    frames = (
        [
            AudioFrameWrapped(
                frame = silent_frame,
                is_from_empty_part = True
            )
        ] * number_of_frames
        if number_of_frames > 0 else
        []
    )

    # The remaining partial silent frames we need
    if number_of_remaining_samples > 0:
        silent_frame = audio_frame_generator.silent(
            sample_rate = audio_fps,
            # TODO: Check where do we get this value from
            layout = layout,
            number_of_samples = number_of_remaining_samples,
            # TODO: Check where do we get this value from
            format = format,
            pts = None,
            time_base = None
        )
        
        frames.append(
            AudioFrameWrapped(
                frame = silent_frame,
                is_from_empty_part = True
            )
        )

    return frames