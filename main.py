from modules import audio, video, tkvideoplayer
import customtkinter as ctk
from customtkinter import filedialog
import datetime
import time
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import os
import pygame
from mutagen.mp3 import MP3
import wave
import shlex


# audio_path = "test_song.wav"
# clips_path = [
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl2.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl3.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl4.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl5.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl6.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl7.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/cute.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/download.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/ulzzang-aesthetic.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/d76296f3436d3000a775932a994515ef.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/6a02ccaab8a4653a97dcd895ce0a1e89.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/a30c97b0066e96dd76a2bc8817d0e27f.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/anime-black.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/ac43f908af0af80aa0d04eba17b20e33.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/b337ece7fdaf7b43ea90414604b2fe32.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/954a13b892968bbb0152404ded0546fa.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/fa06e7189384aa6cfacecd6285d83df9.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/c182c85da3fd30efd88377b00a904dfe.gif",
#     "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/b039e3faf7cc027b06e61926c6d7c7e6.gif",
# ]

# tempo, beat_times, beat_intervals = audio.get_intervals(audio_path)
# clips = video.prepare(clips_path)
# concatenated_video = video.concat_clips(clips, beat_intervals)
# final_video = video.add_audio(concatenated_video, audio_path)

# final_video.write_videofile("test.mp4")


class AudioDropWindow(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Import Audio file")
        self.geometry("500x800")
        self.tempo = None
        self.beat_times = None
        self.beat_intervals = None
        self.audio_file = None

        # -- frames --
        self.frame_1 = ctk.CTkFrame(self)
        self.frame_1.pack(expand=1, fill="both", padx=30, pady=30)

        self.outline = ctk.CTkFrame(
            self.frame_1, border_width=3, fg_color="transparent"
        )
        self.outline.pack(expand=1, fill="both", padx=30, pady=(30, 10))

        # init the outline frame as drop target for dnd
        self.outline.drop_target_register(DND_FILES)
        self.outline.dnd_bind("<<Drop>>", self.drop_event)

        # -- buttons --
        self.audio_file_button = ctk.CTkButton(
            self.frame_1, text="Or select a file", command=self.click_event
        )
        self.audio_file_button.pack(fill="x", padx=30, pady=(0, 30))

        # -- labels --
        self.drop_label = ctk.CTkLabel(self.outline, text="Drop your audio file here")
        self.drop_label.pack(expand=1)

    def click_event(self):
        # openfile dialog if not dnd
        self.audio_file = filedialog.askopenfilename()
        if self.audio_file:
            self.start_audio_analysis(self.audio_file)

    def drop_event(self, event):
        self.audio_file = event.data.strip("{}")
        self.start_audio_analysis(self.audio_file)

    def start_audio_analysis(self, filepath):
        # destroy stuff to make place for the label and progress bar
        self.audio_file_button.destroy()
        self.outline.destroy()

        self.bar_label = ctk.CTkLabel(self.frame_1, text="Preparing audio...")
        self.bar_label.pack()

        self.progress = ctk.CTkProgressBar(self.frame_1)
        self.progress.pack(padx=30, pady=10)
        self.progress.start()

        # new thread to start analizing audio
        threading.Thread(
            target=self.run_audio_analysis, args=(filepath,), daemon=True
        ).start()

    def run_audio_analysis(self, filepath):
        result = audio.get_intervals(filepath)

        # after analizing is done, call function to get rid of everything and destroy the window
        self.after(0, self.analysis_finished, result)

    def analysis_finished(self, result):
        self.progress.stop()
        self.progress.destroy()

        # results being saved into attributes
        self.tempo, self.beat_times, self.beat_intervals = result

        self.destroy()


class GifDropWindow(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Import GIF files")
        self.geometry("500x800")
        self.gif_paths = []

        # -- frames --
        self.frame_1 = ctk.CTkFrame(self)
        self.frame_1.pack(expand=1, fill="both", padx=30, pady=30)

        self.outline = ctk.CTkFrame(
            self.frame_1, border_width=3, fg_color="transparent"
        )
        self.outline.pack(expand=1, fill="both", padx=30, pady=(30, 10))

        # init outline frame as drop target for dnd
        self.outline.drop_target_register(DND_FILES)
        self.outline.dnd_bind("<<Drop>>", self.drop_event)

        # -- buttons --
        self.audio_file_button = ctk.CTkButton(
            self.frame_1, text="Or select files", command=self.click_event
        )
        self.audio_file_button.pack(fill="x", padx=30, pady=(0, 30))

        self.confirm_button = ctk.CTkButton(
            self, text="Roll with those", command=self.destroy
        )

        # -- labels --
        self.drop_label = ctk.CTkLabel(self.outline, text="Drop your GIF files here")
        self.drop_label.pack(expand=1)

    def click_event(self):
        self.gif_paths = filedialog.askopenfilenames()

        for path in self.gif_paths:
            ctk.CTkLabel(self.frame_1, text=path).pack()
        self.confirm_button.pack()

    def drop_event(self, event):
        # handling file preparation cause dnd formats them weirdly
        files = self.tk.splitlist(event.data)
        new_paths = [f.strip("{}") for f in files]

        self.gif_paths.extend(new_paths)

        for path in self.gif_paths:
            ctk.CTkLabel(self.frame_1, text=path).pack()
            print(path) # debug printing
        self.confirm_button.pack()





class App(ctk.CTk):
    def __init__(self, tempo, beat_times, beat_intervals, gifs: list, audio_path):
        super().__init__()
        self.geometry("800x1000")
        self.title("MVMAKER")

        self.tempo = tempo
        self.beat_times = beat_times
        self.beat_intervals = beat_intervals
        self.number_of_intervals = len(beat_intervals)
        self.audio_path = audio_path
        self.gifs = gifs

        # -- Frames --
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.pack_propagate(False)
        self.video_frame.pack(expand=1, fill="both", padx=30, pady=30)

        self.music_frame = ctk.CTkFrame(self)
        self.music_frame.pack_propagate(False)
        self.music_frame.pack(expand=1, fill="both", padx=30, pady=(0, 30))

        self.gif_frame = ctk.CTkFrame(self)
        self.gif_frame.pack_propagate(False)
        self.gif_frame.pack(expand=1, fill="both", padx=30)

        # -- buttons --
        self.generate_button = ctk.CTkButton(
            self, text="Generate Video", command=self.generate
        )
        self.generate_button.pack(padx=30, pady=10)

        # -- video player --
        self.vid_player = video.VideoPlayer(self.video_frame, "test.mp4")
        self.vid_player.pack(expand=1, fill="both")

        # -- music player --
        self.music_player_container = ctk.CTkFrame(self.music_frame)
        self.music_player_container.pack(fill="x", padx=10, pady=10)

        self.music_player = audio.MusicPlayer(self.music_player_container, self.audio_path)
        self.music_player.pack(fill="x")

    def generate(self):
        clips = video.prepare(self.gifs)
        concatenated_video = video.concat_clips(clips, self.beat_intervals)
        final_video = video.add_audio(concatenated_video, self.audio_path)

        final_video.write_videofile("test.mp4")


def main():
    # audio_window = AudioDropWindow()
    # audio_window.mainloop()
    # audio_path = audio_window.audio_file
    # tempo = audio_window.tempo
    # beat_times = audio_window.beat_times
    # beat_intervals = audio_window.beat_intervals

    # gif_window = GifDropWindow()
    # gif_window.mainloop()
    # gifs = gif_window.gif_paths

    # main_window = App(tempo, beat_times, beat_intervals, gifs, audio_path)
    # main_window.mainloop()

    main_window = App(3, [], [2, 3, 54, 6], [], "test_song.wav")
    main_window.mainloop()


if __name__ == "__main__":
    main()
