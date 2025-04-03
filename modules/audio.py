import librosa
import numpy as np
import pygame
import wave
import os
import customtkinter as ctk


class MusicPlayer(ctk.CTkFrame):
    def __init__(self, parent, audio_file, **kwargs):
        super().__init__(parent, **kwargs)
        self.audio_file = audio_file
        self.duration = None

        # get audio duration for wav and mp3
        ext = os.path.splitext(self.audio_file)[1].lower()
        if ext == ".wav":
            with wave.open(self.audio_file, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                self.duration = frames / float(rate)
        elif ext == ".mp3":
            audio = MP3(self.audio_file)
            self.duration = audio.info.length
        else:
            raise ValueError("Unsupported file format")

        # init pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(self.audio_file)

        self.is_playing = False

        # -- button --
        self.play_button = ctk.CTkButton(
            self, text="", command=self.play, width=40, height=40
        )
        self.play_button.pack(side="left", padx=5, pady=5)
        self.stop_button = ctk.CTkButton(
            self, text="", command=self.stop, width=40, height=40
        )
        self.stop_button.pack(side="left", padx=5, pady=5)

        # -- sliders --
        self.progress_slider = ctk.CTkSlider(self, from_=0, to=self.duration)
        self.progress_slider.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.progress_slider.set(0)

        # -- labels --
        self.time_label = ctk.CTkLabel(self, text=self.format_time(0))
        self.time_label.pack(side="left", padx=5, pady=5)

        # start loop
        self.update_progress()

    def play(self):
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.progress_slider.set(0)
        self.time_label.configure(text=self.format_time(0))

    def update_progress(self):
        if self.is_playing:
            current_pos = pygame.mixer.music.get_pos() / 1000.0

            # if current_pos = -1, the song is over
            if current_pos < 0:
                current_pos = self.duration
                self.is_playing = False

            # set slider and label to current progress
            self.progress_slider.set(current_pos)
            self.time_label.configure(text=self.format_time(current_pos))

        # update every 250ms
        self.after(250, self.update_progress)

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        sec = int(seconds % 60)
        return f"{minutes:02d}:{sec:02d}"


def get_intervals(audio_path):
    print("Loading audio...")
    y, sr = librosa.load(audio_path)

    print("Calculating tempo and beat frames...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    print("Calculating beat times...")
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    print("Calculating beat intervals...")
    beat_intervals = np.diff(np.array(beat_times))

    print("BPM:", tempo)
    print("Beat Times:", beat_times)
    print("Beat Intervals:", beat_intervals)

    return tempo, beat_times, beat_intervals
