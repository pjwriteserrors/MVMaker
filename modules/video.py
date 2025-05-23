from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
from moviepy.video.fx.Crop import Crop
from moviepy.video.fx.Loop import Loop
import customtkinter as ctk
from customtkinter import filedialog
import datetime
import threading
from . import tkvideoplayer
import os
import math
from PIL import Image
import pygame


# class VideoPlayer(ctk.CTkFrame):
#     def __init__(self, parent, gifs, beat_intervals, audio_path, duration, **kwargs):
#         super().__init__(parent, fg_color="transparent", **kwargs)
#         self.gifs = gifs
#         self.beat_intervals = beat_intervals
#         self.audio_path = audio_path
#         self.duration = duration
#         self.video_file = None

#         # generate all the widgets
#         self.vid_player = tkvideoplayer.TkinterVideo(
#             scaled=True,
#             master=self,
#             keep_aspect=True,
#             consistant_frame_rate=True,
#             bg="black",
#         )
#         self.vid_player.pack(expand=True, fill="both", padx=10)

#         self.play_pause_video_button = ctk.CTkButton(
#             self,
#             text="",
#             width=40,
#             height=40,
#             command=self.play_pause,
#             state="disabled",
#         )
#         self.play_pause_video_button.pack(anchor="sw", side="left", padx=10, pady=10)

#         self.start_time = ctk.CTkLabel(self, text=str(datetime.timedelta(seconds=0)))
#         self.start_time.pack(anchor="sw", side="left", padx=(0, 10), pady=(0, 15))

#         self.progress_value = ctk.IntVar(self)

#         self.progress_slider = ctk.CTkSlider(
#             self,
#             variable=self.progress_value,
#             orientation="horizontal",
#             width=100,
#             from_=-1,
#             to=1,
#             number_of_steps=1,
#             command=self.seek,
#         )
#         self.progress_slider.pack(
#             anchor="sw", side="left", fill="x", expand=1, padx=(0, 10), pady=(0, 21)
#         )

#         self.end_time = ctk.CTkLabel(self, text=str(datetime.timedelta(seconds=0)))
#         self.end_time.pack(anchor="sw", side="left", padx=(0, 10), pady=(0, 15))

#         # bind player
#         self.vid_player.bind("<<Duration>>", self.update_duration)
#         self.vid_player.bind("<<SecondChanged>>", self.update_scale)
#         self.vid_player.bind("<<Ended>>", self.video_ended)

#     def open_video(self):
#         self.play_pause_video_button.configure(state="normal")
#         self.vid_player.stop()

#         if self.video_file:
#             # load video
#             self.vid_player.load(self.video_file)
#             self.progress_slider.set(-1)

#     def update_duration(self, event):
#         try:
#             duration = int(self.vid_player.video_info()["duration"])
#             self.progress_slider.configure(
#                 from_=-1, to=duration, number_of_steps=duration
#             )
#             self.end_time.configure(text=str(datetime.timedelta(seconds=duration)))
#         except:
#             pass

#     def seek(self, value):
#         if self.video_file:
#             try:
#                 self.vid_player.seek(int(value))
#                 self.vid_player.play()
#                 self.vid_player.after(50, self.vid_player.pause)
#                 self.play_pause_video_button.configure(text="")
#             except:
#                 pass

#     def update_scale(self, event):
#         try:
#             self.progress_slider.set(int(self.vid_player.current_duration()))
#             self.start_time.configure(
#                 text=str(
#                     datetime.timedelta(
#                         seconds=int(self.vid_player.current_duration() + 1)
#                     )
#                 )
#             )
#         except:
#             pass

#     def play_pause(self):
#         if self.video_file:
#             if self.vid_player.is_paused():
#                 self.vid_player.play()
#                 pygame.mixer.music.unpause()
#                 self.play_pause_video_button.configure(text="")

#             else:
#                 self.vid_player.pause()
#                 pygame.mixer.music.pause()
#                 self.play_pause_video_button.configure(text="")

#     def video_ended(self, event):
#         self.play_pause_video_button.configure(text="")
#         self.progress_slider.set(-1)
#         pygame.mixer.music.stop()


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


def concat_clips(clips, intervals, total_duration, clip_duration):
    shortened_clips = []
    current_time = 0
    beat_index = 0
    i = 0

    while current_time < total_duration:
        # 1) calculate how long next clip is shown
        if beat_index < len(intervals):
            skip = clip_duration[i % len(clip_duration)]
            num_intervals = skip + 1
            if beat_index + num_intervals <= len(intervals):
                segment_duration = sum(
                    intervals[beat_index : beat_index + num_intervals]
                )
            else:
                segment_duration = sum(intervals[beat_index:])
            beat_index += num_intervals
        else:
            segment_duration = total_duration - current_time

        duration_to_use = min(segment_duration, total_duration - current_time)

        # 2) pull clip from list
        clip = clips[i % len(clips)]

        # 3) if clip is shorter than duration, loop, otherwise subclip
        if clip.duration >= duration_to_use:
            part = clip.subclipped(0, duration_to_use)
        else:
            looper = Loop(duration=duration_to_use)
            part = looper.apply(clip)

        shortened_clips.append(part)

        current_time += duration_to_use
        i += 1

    return concatenate_videoclips(shortened_clips)


def add_audio(clip, audio_path):
    audioclip = AudioFileClip(audio_path)

    final_video = clip.with_audio(audioclip)

    return final_video



class ThumbnailLabel(ctk.CTkLabel):
    """
    class to get labels with thumbnails of gif
    """

    def __init__(self, master, gif, size=(200, 200), *args, **kwargs):
        # load gif and get thumbnail
        img = Image.open(gif)
        img.thumbnail(size)
        self.thumbnail = ctk.CTkImage(img, size=size)
        super().__init__(master, image=self.thumbnail, text="", *args, **kwargs)
        # reference to self.thumbnail gets saved for gc to not throw away
