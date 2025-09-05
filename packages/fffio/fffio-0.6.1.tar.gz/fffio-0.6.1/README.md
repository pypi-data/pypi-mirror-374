# fffio (FFmpeg Frame Input/Output)

This is a Python package for easily reading and writing video files.

## Install

To install from PyPI:

```bash
pip install fffio
```

To install from GitHub:

```bash
pip install git+https://github.com/yamakox/fffio.git
```

## How to read frames from a video

Simply iterate through calls to the `FrameReader`'s `frames` method.

```python
from fffio import FrameReader
import cv2

with FrameReader('sample.mp4') as reader:
    for i, frame in enumerate(reader.frames(), 1):
        # frame is a numpy.ndarray(shape=(height, width, 3), dtype=np.uint8).
        _ = cv2.imwrite(
            f'sample{i:05d}.jpg', 
            cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        )
```

## How to write frames to a video

Simply iterate through calls to `FrameWriter`'s `write` or `write_frame` method.

```python
from fffio import FrameWriter
import cv2
from pathlib import Path

size=(1920, 1080)
with FrameWriter('sample.mp4', size=size) as writer:
    for file in sorted(Path('.').glob('*.jpg')):
        frame = cv2.cvtColor(cv2.imread(str(file)), cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, size, interpolation=cv2.INTER_LANCZOS4)
        writer.write(frame)
```

`FrameWriter` performs color correction during conversion from RGB to YUV. For more information, please see [Colorspace support in FFmpeg](https://trac.ffmpeg.org/wiki/colorspace#colorspace_yuv420p).

## Examples

The script examples in the `examples` folder can be run using [uv](https://docs.astral.sh/uv/).

```bash
cd examples
uv run frame_writer_sample.py
uv run frame_reader_sample.py
```

## Build

Please see [Build.md](./Build.md).
