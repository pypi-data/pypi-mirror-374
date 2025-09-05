import numpy as np
import ffmpeg
import subprocess
from dataclasses import dataclass
from typing import Union

@dataclass
class Probe:
    '''Probing first video stream from the input video file.

    Args:
        input_file_name (str): input video file name

    Attributes:
        video_file_name (str): input video file name
        width (int): width of video frame
        height (int): height of video frame
        sample_aspect_ratio (str): sample aspect ratio
        display_aspect_ratio (str): display aspect ratio
        duration (float): duration of video in seconds
        fps (float): frames per seconds
        n_frames (int): number of frames
        rotation (int): video rotation
    '''

    video_file_name: str
    width: int
    height: int
    sample_aspect_ratio: str
    display_aspect_ratio: str
    duration: float
    fps: float
    n_frames: int
    rotation: int

    def __init__(self, input_file_name: str):
        self.video_file_name = input_file_name
        probe = ffmpeg.probe(input_file_name)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        self.width = int(video_info['width'])
        self.height = int(video_info['height'])
        self.sample_aspect_ratio = video_info['sample_aspect_ratio'] if 'sample_aspect_ratio' in video_info else None
        self.display_aspect_ratio = video_info['display_aspect_ratio'] if 'display_aspect_ratio' in video_info else None
        self.duration = float(video_info['duration'])
        self.fps = eval(video_info['r_frame_rate'])
        self.n_frames = int(eval('{0}*{1}'.format(video_info['duration'], video_info['r_frame_rate'])))
        self.rotation = 0
        if 'side_data_list' in video_info and len(video_info['side_data_list']):
            if 'rotation' in video_info['side_data_list'][0]:
                self.rotation = int(video_info['side_data_list'][0]['rotation'])


class FrameReader:
    '''Video frame reader from the input video file using ffmpeg.
    
    Args:
        input_file_name (str): input video file name
        ss (float): start time in seconds
        to (float): stop time in seconds, or end time if None is specified
        n_frames (int): number of frames
        filter_complex (dict[str, Union[dict, list, tuple]]): definition of a complex filtergraph
        pix_fmt (str): output pixel format: only "rgb24" (default) or "rgb48" supported

    Attributes:
        video_file_name (str): input video file name
        width (int): width of rotated video frame
        height (int): height of rotated video frame
        pix_fmt (str): output pixel format
    '''

    video_file_name: str
    width: int
    height: int

    def __init__(self, 
                 input_file_name: str, 
                 ss: float = 0, 
                 to: float = None, 
                 n_frames: int = None, 
                 filter_complex: dict[str, Union[dict, list, tuple]] = None, 
                 pix_fmt: str = 'rgb24'):
        if pix_fmt not in ['rgb24', 'rgb48']:
            raise  ValueError('pix_fmt must be "rgb24" or "rgb48"')
        self.pix_fmt = pix_fmt
        self.dtype, self.dbytes = (np.uint8, 1) if pix_fmt == 'rgb24' else (np.uint16, 2)
        self.video_file_name = input_file_name
        self.probe = Probe(input_file_name)
        if int(self.probe.rotation) % 180:
            self.width = self.probe.height
            self.height = self.probe.width
        else:
            self.width = self.probe.width
            self.height = self.probe.height
        if to is None:
            to = self.probe.duration
        process = ffmpeg.input(input_file_name, ss=ss, to=to)
        if n_frames is not None:
            process = process.filter('fps', n_frames / (to - ss))
        if filter_complex:
            for k, v in filter_complex.items():
                if type(v) == dict:
                    process = process.filter_(k, **v)
                elif type(v) == list or type(v) == tuple:
                    process = process.filter_(k, *v)
                else:
                    process = process.filter_(k, v)
        args = (
            process
            .output('pipe:', format='rawvideo', pix_fmt=pix_fmt)
            .compile()
        )
        self.process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def close(self):
        '''Close reader object.
        '''
        try:
            self.process.stdout.close()
            self.process.wait()
        except:
            pass

    def read_frame(self):
        '''Read a frame from the input video file.
        
        Returns:
            np.ndarray: Array of frame buffer which shape is (height, width, 3) and dtype is np.uint8 (rgb24) or np.uint16 (rgb48)
        '''
        in_bytes = self.process.stdout.read(self.probe.width * self.probe.height * 3 * self.dbytes)
        if not in_bytes:
            return None
        return np.frombuffer(in_bytes, self.dtype).reshape([self.height, self.width, 3])

    def frames(self):
        '''Get a generator of input video frames.

        Returns:
            Generator[np.ndarray]: a generator of input video frames
        '''
        while (frame := self.read_frame()) is not None:
            yield frame
