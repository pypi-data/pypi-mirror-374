# Play Videos

- [Introduction](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/video.md#introduction)
- [Video Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/video.md#video-plot)
- [Play YouTube](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/video.md#play-youtube)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide)

## Introduction

- You can **stream videos** directly on terminal with the functions `play_video()` and `play_youtube()`.

- The function `show()` is not necessary in both cases, as it is called internally.

- The **video display size** adapts to the screen size automatically, but you can control it using `plotsize()` before calling video functions.

- **Dynamic sizing**: For optimal viewing, use `plotsize(width, height)` to set video dimensions. The recommended approach is to calculate height as a percentage of width (e.g., 40% ratio) with a minimum height for readability.

- To **download videos** from the given YouTube `url` to the specified `path`, use the `get_youtube()` method.

- Both streaming functions may require further development. Any [bug report](https://github.com/ccmitchellusa/plotext_plus/issues/new) or development idea is welcomed. 

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Play Videos](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/video.md)

## Video Plot

To play a video with audio, use the the `play_video()` function. Set the parameter `from_youtube` to `True` to make sure that the color rendering is correct for videos downloaded from YouTube.

### Basic Video Example

```python
import plotext_plus as plt
path = 'moonwalk.mp4'
plt.download(plt.test_video_url, path)
plt.play_video(path, from_youtube = True)
plt.delete_file(path)
```

### Video with Dynamic Sizing

For better video display with proper aspect ratio:

```python
import plotext_plus as plt
from plotext_plus import utilities as ut

# Download test video
path = 'moonwalk.mp4'
plt.download(plt.test_video_url, path)

# Set optimal video size before playing
# Calculate width based on terminal, height as 40% ratio with minimum
video_width = max(ut.terminal_width() - 6, 50)  # Account for margins
video_height = max(int(video_width * 0.4), 16)  # 40% aspect ratio, minimum 16 rows

plt.plotsize(video_width, video_height)
plt.play_video(path, from_youtube=True)
plt.delete_file(path)
```

or directly on terminal:

```bash
python3 -c "import plotext_plus as plt; path = 'moonwalk.mp4'; plt.download(plt.test_video_url, path); plt.play_video(path, from_youtube = True); plt.delete_file(path)"
```

which will render [this video](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/chart.mp4) on terminal.

More documentation can be accessed with `doc.play_video()`.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Play Videos](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/video.md)

## Play YouTube

To play a YouTube video from `url` use the function `play_youtube()`, as in this example:

```python
import plotext_plus as plt
plt.play_youtube(plt.test_youtube_url)
```

or directly on terminal:

```console
python3 -c "import plotext_plus as plt; plt.play_youtube(plt.test_youtube_url)"
```

which will render [this youtube video](https://www.youtube.com/watch?v=ZNAvVVc4b3E&t=75s) on terminal. 

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Play Videos](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/video.md)