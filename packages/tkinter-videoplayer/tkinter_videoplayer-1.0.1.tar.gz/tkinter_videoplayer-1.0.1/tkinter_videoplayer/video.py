import cv2
from PIL import Image, ImageTk
import tkinter as tk
import time

from .events import EventDispatcher


class Video(EventDispatcher):
    def __init__(self, parent, width=640, height=480, loop=False, show_fps=False):
        super().__init__()
        self.parent = parent
        self.width = width
        self.height = height
        self.cap = None
        self.playing = False
        self.paused = False
        self.frame = tk.Frame(parent, width=width, height=height, bg="black")
        self.frame.pack_propagate(False)
        self.video_img = tk.Label(self.frame, bg="black")
        self.video_img.pack(fill=tk.BOTH, expand=1)
        self.show_fps = show_fps
        self.fps_label = None
        if self.show_fps:
            self.fps_label = tk.Label(self.frame, fg="#888", bg="black", font=("Arial", 8), anchor="ne")
            self.fps_label.place(relx=1.0, rely=0.0, anchor="ne")
        self._frame_times = []  # For FPS measurement
        self.thread = None
        self.frame_pos = 0
        self.video_path = None
        self.loop = loop

        def bubble_event_to_top(event, event_type):
            parent_frame = self.frame.master
            if isinstance(parent_frame, tk.Frame):
                parent_frame.event_generate(event_type, x=event.x, y=event.y)

        def bind_event(btn):
            self.video_img.bind(btn, lambda e, btn=btn: bubble_event_to_top(e, btn))

        for btn in ("<Button-1>", "<Button-2>", "<Enter>", "<Leave>", "<Key-space>"):
            bind_event(btn)

        # Bind resize event
        self.frame.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        # Pause video if playing during resize to prevent crash
        was_playing = self.playing and not self.paused
        if was_playing:
            self.paused = True
            time.sleep(0.1)  # Allow play thread to pause
        new_w, new_h = event.width, event.height
        if new_w != self.width or new_h != self.height:
            self.width, self.height = new_w, new_h
            self._display_current_frame()
        # Resume video if it was playing before resize
        if was_playing:
            self.paused = False

    def load(self, video_path):
        self.stop()
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        self.frame_pos = 0
        self.dispatch_event("load")

    def _cancel_play_loop_callback(self):
        if hasattr(self, "_play_loop_callback_id") and self._play_loop_callback_id:
            self.parent.after_cancel(self._play_loop_callback_id)
            self._play_loop_callback_id = None

    def play(self):
        if not self.cap and self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)

        self._cancel_play_loop_callback()

        # Handle resuming from pause state
        if self.playing and self.paused:
            self.paused = False
            self._frame_times.clear()
            self._play_loop_tk()  # Restart play loop to advance frames
            self.dispatch_event("play")
            return

        # If already playing and not paused, nothing to do
        if self.playing and not self.paused:
            return

        # Start a new playback
        self.playing = True
        self.paused = False
        self._play_loop_callback_id = None
        self._frame_times.clear()
        self._play_loop_tk()
        self.dispatch_event("play")

    def restart_loop(self):
        # Restart playback from the beginning for looping, without releasing or recreating cap.
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.frame_pos = 0
        self.playing = True
        self.paused = False
        # Do not stop the play loop, just reset frame position

    def pause(self):
        self.paused = True
        self.dispatch_event("pause")

    def stop(self):
        self.playing = False
        self.paused = False
        self._cancel_play_loop_callback()
        if self.cap:
            self.cap.release()
            self.cap = None
        # Only update label if it still exists
        if self.video_img.winfo_exists():
            self.video_img.config(image="")
        # Trigger pause event when stopping
        self.dispatch_event("pause")

    @property
    def currentTime(self):
        """Get or set the current playback time in seconds."""
        if not self.cap:
            return 0.0
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        return frame / fps if fps > 0 else 0.0

    @currentTime.setter
    def currentTime(self, seconds):
        if not self.cap:
            return
        was_playing = self.playing and not self.paused
        if was_playing:
            self.paused = True
            time.sleep(0.1)  # Allow thread to pause
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(seconds * fps) if fps > 0 else 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.frame_pos = frame_number
        # If paused, display the frame immediately
        if not was_playing or self.paused:
            self._display_current_frame()
        if was_playing:
            self.paused = False

    @property
    def duration(self):
        """Get the duration of the video in seconds."""
        if not self.cap:
            return 0.0
        frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        return frame_count / fps if fps > 0 else 0.0

    def _play_loop_tk(self):
        if not self.playing or not self.cap or not self.cap.isOpened():
            self.stop()
            return
        if self.paused:
            self._play_loop_callback_id = self.parent.after(50, self._play_loop_tk)
            return
        self._display_current_frame(advance=True)
        # Schedule next frame update and track callback ID
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / max(fps, 25))
        self._play_loop_callback_id = self.parent.after(delay, self._play_loop_tk)

    def _display_current_frame(self, advance=False):
        """
        Optimized: Use OpenCV for resizing and minimize conversions to PIL for lower memory and latency.
        """
        if not self.cap:
            return

        def handle_video_end():
            self.playing = False
            self.paused = False
            self.frame_pos = 0
            self._cancel_play_loop_callback()
            self.dispatch_event("ended")

        if advance:
            ret, frame = self.cap.read()
            if not ret:
                if getattr(self, "loop", False):
                    # If looping, seek to start and continue
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.frame_pos = 0
                    ret, frame = self.cap.read()
                    if not ret:
                        handle_video_end()
                        return
                else:
                    handle_video_end()
                    return
            self.frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        else:
            pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            ret, frame = self.cap.read()
            if not ret:
                return
            if int(pos) != self.frame_pos:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_pos)
                ret, frame = self.cap.read()
                if not ret:
                    return

        # Calculate aspect ratio preserving size
        orig_h, orig_w = frame.shape[:2]
        target_w, target_h = self.width, self.height
        scale = min(target_w / orig_w, target_h / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        # Use OpenCV for resizing (faster than PIL)
        frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Create black background and paste resized image centered
        bg = cv2.cvtColor(
            cv2.copyMakeBorder(
                frame_resized,
                top=(target_h - new_h) // 2,
                bottom=(target_h - new_h + 1) // 2,
                left=(target_w - new_w) // 2,
                right=(target_w - new_w + 1) // 2,
                borderType=cv2.BORDER_CONSTANT,
                value=[0, 0, 0],
            ),
            cv2.COLOR_BGR2RGB,
        )

        # Convert to PIL only for final display
        img = Image.fromarray(bg)
        imgtk = ImageTk.PhotoImage(image=img)

        if self.video_img.winfo_exists():
            self.video_img.imgtk = imgtk
            self.video_img.config(image=imgtk)
        # FPS overlay logic
        if self.show_fps and self.fps_label:
            now = time.time()
            self._frame_times.append(now)
            # Keep only last 10 frame times
            if len(self._frame_times) > 10:
                self._frame_times.pop(0)
            if len(self._frame_times) >= 2:
                elapsed = self._frame_times[-1] - self._frame_times[0]
                fps = (len(self._frame_times) - 1) / elapsed if elapsed > 0 else 0.0
                self.fps_label.config(text=f"{fps:.1f} fps")
            else:
                self.fps_label.config(text="")
