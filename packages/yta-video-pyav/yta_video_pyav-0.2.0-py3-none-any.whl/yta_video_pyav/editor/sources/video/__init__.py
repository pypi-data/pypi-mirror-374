"""
Video sources, that are the source from
where we will obtain the data to offer
as video in our editor.

These sources will be used by other
classes to access to the frames but 
improve the functionality and simplify
it.
"""
from yta_video_pyav.editor.sources.abstract import _VideoSource
from yta_video_pyav.editor.utils.frame_generator import VideoFrameGenerator
from yta_video_pyav.reader import VideoReader
from yta_validation import PythonValidator
from av.video.frame import VideoFrame
from PIL import Image
from quicktions import Fraction
from typing import Union

import numpy as np


class VideoFileSource(_VideoSource):
    """
    Class to represent a video, read from a
    video file, as a video media source.
    """

    @property
    def copy(
        self
    ) -> 'VideoFileSource':
        """
        Get a copy of this instance.
        """
        return VideoFileSource(self.filename)

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
        return self.reader.duration
    
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
        filename: str
    ):
        # TODO: Validate the 'filename' is actually
        # a valid and readable video file

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

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment, using the video cache system, read
        from the file.
        """
        return self.reader.get_frame(t)
    
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction] = None
    ):
        """
        Get the video frame with the given 't' time
        moment, using the video cache system, read
        from the file.
        """
        return self.reader.get_audio_frames_at_t(t, video_fps)

class VideoImageSource(_VideoSource):
    """
    Class to represent a video, made from an
    image, as a video media source.

    This source is static. The same video
    frame will be returned always.
    """

    @property
    def copy(
        self
    ) -> 'VideoImageSource':
        """
        Get a copy of this instance.
        """
        return VideoImageSource(
            filename = self.filename,
            do_include_alpha = self._do_include_alpha
        )

    @property
    def duration(
        self
    ):
        """
        The duration of the source.
        """
        # TODO: Should I return something like 999 (?)
        return None

    @property
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        # By default we use it accepting transparency
        # TODO: The image must be like this:
        # arr = np.array(img)  # shape (h, w, 4), dtype=uint8
        # TODO: What value if no alpha (?)
        return VideoFrame.from_ndarray(self._image, format = 'rgba')

    def __init__(
        self,
        filename: str,
        # TODO: Do I need the size (?)
        #size: tuple[int, int] = (1920, 1080),
        do_include_alpha: bool = True,
    ):
        # TODO: Validate 'filename' is a valid
        # and readable image file

        self.filename: str = filename
        """
        The filename of the original image.
        """
        self._do_include_alpha: bool = do_include_alpha
        """
        The internal flag to indicate if we
        want to consider the alpha channel or
        not.
        """

        image = (
            image_to_numpy_pillow(image, do_include_alpha = do_include_alpha)
            if PythonValidator.is_string(image) else
            image
        )

        self._image: np.ndarray = image
        """
        The image that will be used to make the
        frame that will be played its whole
        duration.
        """

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment.
        """
        # TODO: I keep this method to have the same
        # in all the clases, but it makes no sense
        # because it is the property itself and the
        # 't' parameter is ignored
        return self.frame
    
class VideoColorSource(_VideoSource):
    """
    Class to represent a video, made from a
    static color, as a video media source.

    This source is static. The same video
    frame will be returned always.
    """

    @property
    def copy(
        self
    ) -> 'VideoColorSource':
        """
        Get a copy of this instance.
        """
        return VideoColorSource(
            color = self._color,
            size = self.size
        )

    @property
    def duration(
        self
    ):
        """
        The duration of the source.
        """
        # TODO: Should I return something like 999 (?)
        return None

    @property
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        return VideoFrameGenerator().background.full_white(
            size = self.size
        )

    def __init__(
        self,
        # TODO: Apply format to 'color'
        color: any,
        size: tuple[int, int] = (1920, 1080),
        # TODO: Do I need this (?)
        # dtype: dtype = np.uint8,
        # format: str = 'rgb24',
    ):
        # TODO: Apply format to 'color'
        self._color: any = color
        """
        The color that will be used to make the
        frame that will be played its whole
        duration.
        """
        self.size: tuple[int, int] = size
        """
        The size of the media frame.
        """

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment.
        """
        # TODO: I keep this method to have the same
        # in all the clases, but it makes no sense
        # because it is the property itself and the
        # 't' parameter is ignored
        return self.frame
    
class VideoNumpySource(_VideoSource):
    """
    Class to represent a video, made from a
    numpy array, as a video media source.

    This source is static. The same video
    frame will be returned always.
    """

    @property
    def copy(
        self
    ) -> 'VideoNumpySource':
        """
        Get a copy of this instance.
        """
        return VideoNumpySource(
            array = self._array,
            fps = self.fps,
            duration = self.duration
        )

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
    # a 'size' property with the size of the
    # array
    @property
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        # By default we use it accepting transparency
        # TODO: The image must be like this:
        # arr = np.array(img)  # shape (h, w, 4), dtype=uint8
        # TODO: What value if no alpha (?)
        return VideoFrame.from_ndarray(self._array, format = 'rgba')

    def __init__(
        self,
        array: np.ndarray,
        fps: Union[int, float, Fraction] = 60,
        duration: Union[int, float, Fraction] = 1,
    ):
        self._array: np.ndarray = array
        """
        The array of information that will be
        used to make the frame that will be
        played its whole duration.
        """
        self.fps: Fraction = Fraction(fps)
        """
        The frames per second of this video source.
        """
        self.duration: Fraction = Fraction(duration)
        """
        The duration of this video source.
        """

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment.
        """
        # TODO: I keep this method to have the same
        # in all the clases, but it makes no sense
        # because it is the property itself and the
        # 't' parameter is ignored
        return self.frame

    



# TODO: I think I have this util in another
# library, so please check it...
def image_to_numpy_pillow(
    filename: str,
    do_include_alpha: bool = True
) -> 'np.ndarray':
    """
    Read the imagen file 'filename' and transform
    it into a numpy, reading also the alpha channel.
    """
    mode = (
        'RGBA'
        if do_include_alpha else
        'RGB'
    )

    return np.array(Image.open(filename).convert(mode))

"""
The pyav uses Pillow to load an image as
a numpy array but using not the alpha.
"""