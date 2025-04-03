from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
from moviepy.video.fx.Crop import Crop
import customtkinter as ctk
import datetime
from . import tkvideoplayer

class VideoPlayer(ctk.CTkFrame):
    def __init__(self, parent, video_file, **kwargs):
        super().__init__(parent, **kwargs)

        self.generate_preview_button = ctk.CTkButton(
            self,
            text="Generate Preview Video",
        )
        self.generate_preview_button.pack(fill="x", padx=10, pady=10)

        self.vid_player = tkvideoplayer.TkinterVideo(scaled=True, master=self)
        self.vid_player.pack(expand=True, fill="both", padx=10)

        self.play_pause_video_button = ctk.CTkButton(
            self,
            text="",
            width=40,
            height=40,
        )
        self.play_pause_video_button.pack(anchor="sw", side="left", padx=10, pady=10)

        self.progress_video_slider = ctk.CTkSlider(
            self,
            orientation="horizontal",
            width=100,
            from_=0,
            to=100,
            number_of_steps=100,
        )
        self.progress_video_slider.pack(
            anchor="sw", side="left", fill="x", expand=1, padx=(0, 10), pady=(0, 21)
        )

        self.progress_value = ctk.IntVar(self)
        self.progress_label = ctk.CTkLabel(
            self, text=str(datetime.timedelta(seconds=0))
        )
        self.progress_label.pack(anchor="sw", side="left", padx=(0, 10), pady=(0, 15))

    def load_video(): ...


def prepare(gifs):
    formatted_clips = []

    for gif in gifs:
        print("Loading GIF:", gif)
        gif_clip = VideoFileClip(gif)

        print("Resizing GIF:", gif)
        og_width, og_height = gif_clip.size

        resized_clip = gif_clip.resized(height=1920)

        cropper = Crop(
            width=1080,
            height=1920,
            x_center=resized_clip.w / 2,
            y_center=resized_clip.h / 2,
        )

        final_clip = cropper.apply(resized_clip)

        formatted_clips.append(final_clip)

    return formatted_clips


def concat_clips(clips, intervals):
    shortened_clips = []
    for clip in clips:
        for interval in intervals:
            shortened_clip = clip.subclipped(end_time=interval)

        shortened_clips.append(shortened_clip)

    concatenated_video = concatenate_videoclips(shortened_clips)

    return concatenated_video


def add_audio(clip, audio_path):
    audioclip = AudioFileClip(audio_path)

    final_video = clip.with_audio(audioclip)

    return final_video
