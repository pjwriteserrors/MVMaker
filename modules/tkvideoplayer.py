import gc
import av
import time
import threading
import logging
import tkinter as tk
from PIL import ImageTk, Image, ImageOps
from typing import Tuple, Dict

logging.getLogger('libav').setLevel(logging.ERROR)  # Remove warnings about deprecated pixel formats

class TkinterVideo(tk.Label):
    def __init__(self, master, scaled: bool = True, consistant_frame_rate: bool = True, keep_aspect: bool = False, *args, **kwargs):
        super(TkinterVideo, self).__init__(master, *args, **kwargs)
        self.path = ""
        self._load_thread = None

        self._paused = True
        self._stop = True

        self.consistant_frame_rate = consistant_frame_rate  # Try to keep a consistent frame rate

        self._container = None

        self._current_img = None
        self._current_frame_Tk = None
        self._frame_number = 0
        self._time_stamp = 0

        self._current_frame_size = (0, 0)

        self._seek = False
        self._seek_sec = 0

        self._video_info = {
            "duration": 0,    # total video duration in seconds
            "framerate": 0,   # video frame rate
            "framesize": (0, 0)  # (width, height) of the video frames
        }

        self.set_scaled(scaled)
        self._keep_aspect_ratio = keep_aspect
        self._resampling_method: int = Image.NEAREST

        self.bind("<<Destroy>>", self.stop)
        self.bind("<<FrameGenerated>>", self._display_frame)

    def keep_aspect(self, keep_aspect: bool):
        """Keep the aspect ratio when resizing the image."""
        self._keep_aspect_ratio = keep_aspect

    def set_resampling_method(self, method: int):
        """Set the resampling method when resizing."""
        self._resampling_method = method

    def set_size(self, size: Tuple[int, int], keep_aspect: bool = False):
        """Set the target frame size for the video."""
        self.set_scaled(False, self._keep_aspect_ratio)
        self._current_frame_size = size
        self._keep_aspect_ratio = keep_aspect

    def _resize_event(self, event):
        self._current_frame_size = event.width, event.height
        if self._paused and self._current_img and self.scaled:
            if self._keep_aspect_ratio:
                proxy_img = ImageOps.contain(self._current_img.copy(), self._current_frame_size)
            else:
                proxy_img = self._current_img.copy().resize(self._current_frame_size)
            self._current_imgtk = ImageTk.PhotoImage(proxy_img)
            self.config(image=self._current_imgtk)

    def set_scaled(self, scaled: bool, keep_aspect: bool = False):
        self.scaled = scaled
        self._keep_aspect_ratio = keep_aspect
        if scaled:
            self.bind("<Configure>", self._resize_event)
        else:
            self.unbind("<Configure>")
            self._current_frame_size = self.video_info()["framesize"]

    def _set_frame_size(self, event=None):
        """Set frame size based on the video's native resolution."""
        self._video_info["framesize"] = (self._container.streams.video[0].width, self._container.streams.video[0].height)
        self.current_imgtk = ImageTk.PhotoImage(Image.new("RGBA", self._video_info["framesize"], (255, 0, 0, 0)))
        self.config(width=150, height=100, image=self.current_imgtk)

    def _load(self, path):
        """Load and decode the video in a separate thread."""
        current_thread = threading.current_thread()

        try:
            with av.open(path) as self._container:
                # Set automatic thread usage for the stream
                self._container.streams.video[0].thread_type = "AUTO"
                stream = self._container.streams.video[0]

                try:
                    # Get frame rate from the video (average_rate might vary)
                    self._video_info["framerate"] = int(stream.average_rate)
                except TypeError:
                    raise TypeError("Not a video file")

                try:
                    # Calculate video duration in seconds
                    self._video_info["duration"] = float(stream.duration * stream.time_base)
                    self.event_generate("<<Duration>>")
                except (TypeError, tk.TclError):
                    pass

                self._frame_number = 0
                self._set_frame_size()
                self.stream_base = stream.time_base

                try:
                    self.event_generate("<<Loaded>>")
                except tk.TclError:
                    pass

                # Fixed time per frame (in seconds) based on frame rate
                frame_delay = 1.0 / self._video_info["framerate"]
                next_frame_time = time.time() + frame_delay

                while self._load_thread == current_thread and not self._stop:
                    if self._seek:
                        # Seek to specified second; av.open expects microseconds
                        self._container.seek(self._seek_sec * 1000000, backward=True, any_frame=False)
                        self._seek = False
                        self._frame_number = self._video_info["framerate"] * self._seek_sec
                        self._seek_sec = 0

                    if self._paused:
                        time.sleep(0.001)
                        continue

                    try:
                        frame = next(self._container.decode(video=0))
                        self._time_stamp = float(frame.pts * stream.time_base)
                        width = self._current_frame_size[0]
                        height = self._current_frame_size[1]
                        if self._keep_aspect_ratio:
                            im_ratio = frame.width / frame.height
                            dest_ratio = width / height
                            if im_ratio != dest_ratio:
                                if im_ratio > dest_ratio:
                                    new_height = round(frame.height / frame.width * width)
                                    height = new_height
                                else:
                                    new_width = round(frame.width / frame.height * height)
                                    width = new_width

                        self._current_img = frame.to_image(width=width, height=height, interpolation="FAST_BILINEAR")
                        self._frame_number += 1
                        self.event_generate("<<FrameGenerated>>")
                        if self._frame_number % self._video_info["framerate"] == 0:
                            self.event_generate("<<SecondChanged>>")
                    except (StopIteration, av.error.EOFError, tk.TclError):
                        break

                    # Fixed timing: wait until the next scheduled frame time
                    next_frame_time += frame_delay
                    sleep_time = next_frame_time - time.time()
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                self._container.close()
            if self._container:
                self._container.close()
                self._container = None
        finally:
            self._cleanup()
            gc.collect()

    def _cleanup(self):
        self._frame_number = 0
        self._paused = True
        self._stop = True
        if self._load_thread:
            self._load_thread = None
        if self._container:
            self._container.close()
            self._container = None
        try:
            self.event_generate("<<Ended>>")
        except tk.TclError:
            pass

    def load(self, path: str):
        """Loads the video from the specified path."""
        self.stop()
        self.path = path

    def stop(self):
        """Stops the video playback."""
        self._paused = True
        self._stop = True
        self._cleanup()

    def pause(self):
        """Pauses the video."""
        self._paused = True

    def play(self):
        """Starts video playback."""
        self._paused = False
        self._stop = False
        if not self._load_thread:
            self._load_thread = threading.Thread(target=self._load, args=(self.path,), daemon=True)
            self._load_thread.start()

    def is_paused(self):
        """Returns whether the video is paused."""
        return self._paused

    def video_info(self) -> Dict:
        """Returns a dictionary containing duration, frame rate, and frame size."""
        return self._video_info

    def metadata(self) -> Dict:
        """Returns available metadata."""
        if self._container:
            return self._container.metadata
        return {}

    def current_frame_number(self) -> int:
        """Returns the current frame number."""
        return self._frame_number

    def current_duration(self) -> float:
        """Returns the current playback time in seconds."""
        return self._time_stamp

    def current_img(self) -> Image:
        """Returns the current frame as a PIL Image."""
        return self._current_img

    def _display_frame(self, event):
        """Displays the current frame in the label."""
        try:
            # If the image size is the same, paste directly; otherwise create a new PhotoImage.
            if self.current_imgtk.width() == self._current_img.width and self.current_imgtk.height() == self._current_img.height:
                self.current_imgtk.paste(self._current_img)
            else:
                self.current_imgtk = ImageTk.PhotoImage(self._current_img)
            self.config(image=self.current_imgtk)
        except Exception as e:
            # Ignore errors in displaying the frame
            pass

    def seek(self, sec: int):
        """Seeks to the specified second in the video."""
        self._seek = True
        self._seek_sec = sec
