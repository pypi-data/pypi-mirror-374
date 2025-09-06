# tkinter-videoplayer

A simple video player component for Tkinter, built with OpenCV and Pillow.

The current alternatives either didn't work (outdated dependencies) or used `av` (which requires compilation).

## Features
- Batteries included: Includes controls to play, pause, stop, and seek video files
- Familiar UI: Toggle play/pause with a button or click or spacebar
- Easy to install: Doesn't use `av` (which requires compilation on the host system)
- Looks decent visually, and can be customized in `theme.py`
- Works by rendering frames using OpenCV and Pillow

## Screenshot
<img height="220" alt="screenshot" src="https://github.com/user-attachments/assets/81a93dbf-fb35-49e0-a50b-0cc5bb2ef6df" />





## Installation
```bash
pip install tkinter-videoplayer
```

## Quick Start

```python
from tkinter_videoplayer import VideoPlayer
import tkinter as tk

root = tk.Tk()
player = VideoPlayer(root, video_path='sample.mp4', height=360)
root.mainloop()
```

## API

### `VideoPlayer(parent, video_path, **options)`

- `parent`: Tkinter parent widget
- `video_path`: Path to the video file
- `**options`: Additional options to customize the player:
   - `autoplay` (bool): Start playback automatically when loaded. Default: `False`.
   - `loop` (bool): Loop the video when it reaches the end. Default: `False`.
   - `controls` (bool): Show playback controls (play, pause, seek, etc.). Default: `True`.
   - `width` (int): Width of the video player in pixels. Default: video width or parent width.
   - `height` (int): Height of the video player in pixels. Default: video height or parent height.

You can also edit the default theme by modifying `theme.py`.

#### Methods
- `play()`: Start or resume playback
- `pause()`: Pause playback
- `stop()`: Stop playback and reset

#### Properties
- `autoplay` (bool): Whether playback starts automatically when loaded.
- `loop` (bool): Whether playback loops when the video ends.
- `controls` (bool): Whether playback controls are shown.
- `currentTime` (float): Current playback time in seconds (get/set).
- `duration` (float): Duration of the loaded video in seconds (read-only).

#### Events
- `play`: Called when playback starts
- `pause`: Called when playback pauses
- `ended`: Called when playback ends
- `load`: Called when the video loads

## Usage Example
See the [examples](examples/) folder for more examples!

- **01_combined_examples.py**: Shows four different video player configurations in a single 2x2 grid window, each with a title, video, and code snippet.
- **02_events.py**: Demonstrates how to use event listeners for play, pause, and end events.
- **03_external_controls.py**: Shows how to control the video player externally with custom buttons.

```python
# Example: Basic usage
from tkinter_videoplayer import VideoPlayer
import tkinter as tk

root = tk.Tk()
player = VideoPlayer(root, video_path='sample.mp4', height=360)
player.frame.pack()
root.mainloop()
```

```python
# Example: Adding event listeners (see 02_events.py)
def handle_play():
    print("Video started!")
def handle_pause():
    print("Video paused.")
def handle_ended():
    print("Video ended.")

player.add_event_listener("play", handle_play)
player.add_event_listener("pause", handle_pause)
player.add_event_listener("ended", handle_ended)
```

```python
# Example: External controls (see 03_external_controls.py)
btn_play = tk.Button(root, text="Play", command=player.play)
btn_pause = tk.Button(root, text="Pause", command=player.pause)
btn_stop = tk.Button(root, text="Stop", command=player.stop)
btn_play.pack()
btn_pause.pack()
btn_stop.pack()
```
