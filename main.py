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
import json


audio_path = "test_song.wav"
clips_path = [
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl2.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl3.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl4.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl5.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl6.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl7.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/cute.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/download.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/ulzzang-aesthetic.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/d76296f3436d3000a775932a994515ef.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/6a02ccaab8a4653a97dcd895ce0a1e89.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/a30c97b0066e96dd76a2bc8817d0e27f.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/anime-black.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/ac43f908af0af80aa0d04eba17b20e33.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/b337ece7fdaf7b43ea90414604b2fe32.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/954a13b892968bbb0152404ded0546fa.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/fa06e7189384aa6cfacecd6285d83df9.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/c182c85da3fd30efd88377b00a904dfe.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/GRAVES/b039e3faf7cc027b06e61926c6d7c7e6.gif",
]

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
        self.duration = None
        self.total_gifs = None

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
        (
            self.tempo,
            self.beat_times,
            self.beat_intervals,
            self.duration,
            self.total_gifs,
        ) = result

        self.destroy()


# class GifDropWindow(TkinterDnD.Tk):
#     def __init__(self, beat_times, total_gifs):
#         super().__init__()
#         self.title("Import GIF files")
#         self.geometry("500x800")
#         self.gif_paths = []
#         self.beat_times = beat_times

#         # -- frames --
#         self.frame_1 = ctk.CTkFrame(self)
#         self.frame_1.pack(expand=1, fill="both", padx=30, pady=30)

#         self.outline = ctk.CTkFrame(
#             self.frame_1, border_width=3, fg_color="transparent"
#         )
#         self.outline.pack(expand=1, fill="both", padx=30, pady=(30, 10))

#         # init outline frame as drop target for dnd
#         self.outline.drop_target_register(DND_FILES)
#         self.outline.dnd_bind("<<Drop>>", self.drop_event)

#         # -- buttons --
#         self.audio_file_button = ctk.CTkButton(
#             self.frame_1, text="Or select files", command=self.click_event
#         )
#         self.audio_file_button.pack(fill="x", padx=30, pady=(0, 30))

#         self.confirm_button = ctk.CTkButton(
#             self, text="Roll with those", command=self.destroy
#         )

#         # -- labels --
#         self.drop_label = ctk.CTkLabel(
#             self.outline,
#             text=f"Drop your GIF files here\nTotal GIFs needed: {total_gifs}",
#         )
#         self.drop_label.pack(expand=1)

#     def click_event(self):
#         self.gif_paths = filedialog.askopenfilenames()

#         for path in self.gif_paths:
#             ctk.CTkLabel(self.frame_1, text=path).pack()
#         self.confirm_button.pack()

#     def drop_event(self, event):
#         # handling file preparation cause dnd formats them weirdly
#         files = self.tk.splitlist(event.data)
#         new_paths = [f.strip("{}") for f in files]

#         self.gif_paths.extend(new_paths)

#         for path in self.gif_paths:
#             ctk.CTkLabel(self.frame_1, text=path).pack()
#             print(path)  # debug printing
#         self.confirm_button.pack()


class App(ctk.CTk):
    def __init__(self, tempo, beat_times, beat_intervals, audio_path, duration, total_gifs):
        super().__init__()
        self.attributes("-zoomed", True)
        self.title("MVMAKER")

        self.tempo = tempo
        self.beat_times = beat_times
        self.beat_intervals = beat_intervals
        self.number_of_intervals = len(beat_intervals)
        self.audio_path = audio_path
        self.gifs = []
        self.duration = duration
        self.total_gifs = total_gifs

        # init pygame mixer
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(self.audio_path)

        # -- Frames --
        self.video_frame = ctk.CTkFrame(self, width=550)
        self.video_frame.pack_propagate(False)
        self.video_frame.pack(fill="both", pady=30, padx=(5, 30), side="right")

        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side="left", fill="both", expand=1)

        self.music_frame = ctk.CTkFrame(self.left_frame, height=300)
        self.music_frame.pack_propagate(False)
        self.music_frame.pack(side="top", fill="both", padx=(30, 5), pady=(30, 5))

        self.fx_frame = ctk.CTkFrame(self.left_frame)
        self.fx_frame.pack_propagate(False)
        self.fx_frame.pack(
            side="left", padx=(30, 5), pady=(5, 30), fill="both", expand=1
        )

        self.gif_frame = ctk.CTkFrame(self.left_frame)
        self.gif_frame.pack_propagate(False)
        self.gif_frame.pack(
            side="left", padx=(5, 5), pady=(5, 30), fill="both", expand=1
        )

        # -- Buttons --
        self.gif_import_button = ctk.CTkButton(
            self.gif_frame, text="Import your GIFs", command=self.choose_gifs
        )
        self.gif_import_button.pack()

        self.generate_button = ctk.CTkButton(
            self.gif_frame,
            text="Generate Video",
            command=self.generate_button_click,
            state="disabled",
        )
        self.generate_button.pack(fill="x", padx=10, pady=10)

        self.pinterest_random_gifs_button = ctk.CTkButton(
            self.video_frame, text="Feelin' Lucky", command=self.get_pinterest_gifs
        )
        self.pinterest_random_gifs_button.pack()

        # load patterns
        with open("options/patterns.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.skip_beat_frame = ctk.CTkScrollableFrame(
            self.music_frame, fg_color="transparent", orientation="horizontal"
        )

        # -- music player --
        self.music_player_container = ctk.CTkFrame(self.music_frame)
        self.music_player_container.pack(fill="x", padx=10, pady=(10, 0))
        self.music_player = audio.MusicPlayer(
            self.music_player_container, self.audio_path
        )
        self.music_player.pack(fill="x")

        # -- dropdowns --
        # show skip beat frame after music player
        self.skip_beat_frame.pack(expand=1, fill="both", padx=10)

        # dropdown to skip beats for all clips
        self.pair_frame = ctk.CTkFrame(self.skip_beat_frame, corner_radius=0)
        self.pair_frame.pack(side="left", padx=5, pady=(0, 5), expand=1, fill="both")

        self.thumb_label = ctk.CTkLabel(
            self.pair_frame, text="All Clips", width=160, height=160
        )
        self.thumb_label.pack(side="top", pady=(0, 5))

        self.all_beatskip_dropdown = ctk.CTkOptionMenu(
            self.pair_frame,
            values=[str(i) for i in range(len(self.beat_intervals))],
            command=self.set_all_durations,
        )
        self.all_beatskip_dropdown.pack(side="top", pady=(0, 5), padx=5)

        # options dropdown for more variations
        self.pair_frame = ctk.CTkFrame(self.skip_beat_frame, corner_radius=0)
        self.pair_frame.pack(side="left", padx=5, pady=(0, 5), expand=1, fill="both")

        self.thumb_label = ctk.CTkLabel(
            self.pair_frame, text="Cool options", width=160, height=160
        )
        self.thumb_label.pack(side="top", pady=(0, 5))

        self.patterns_beatskip_dropdown = ctk.CTkOptionMenu(
            self.pair_frame,
            values=list(self.data),
            command=self.set_patterns,
        )
        self.patterns_beatskip_dropdown.pack(
            side="left", anchor="n", padx=5, pady=(0, 5)
        )

        # save pattern button
        self.save_pattern_button = ctk.CTkButton(
            self.pair_frame,
            text="Save pattern",
            command=self.get_save_pattern_name,
            width=70,
        )
        self.save_pattern_button.pack(side="left", anchor="n", padx=5, pady=(0, 5))

        self.delete_pattern_button = ctk.CTkButton(
            self.pair_frame,
            text="Delete pattern",
            command=self.delete_pattern,
            width=70,
        )
        self.delete_pattern_button.pack(side="left", anchor="n", padx=5, pady=(0, 5))

        # entry for pattern name
        self.pattern_name_entry = ctk.CTkEntry(
            self.pair_frame, placeholder_text="Name of the pattern"
        )

        # second button for final save
        self.final_save_button = ctk.CTkButton(
            self.pair_frame, text="Save!", command=self.save_pattern
        )

    def hot_load(self, gifs):
        # create pairs of thumbnail and dropdown
        for gif in gifs:
            self.pair_frame = ctk.CTkFrame(self.skip_beat_frame, corner_radius=0)
            self.pair_frame.pack(side="left", padx=5, pady=(0, 5), fill="both")

            self.thumb_label = video.ThumbnailLabel(
                self.pair_frame, gif, size=(160, 160)
            )
            self.thumb_label.pack(side="top", pady=(0, 5))

            self.beatskip_dropdown = ctk.CTkOptionMenu(
                self.pair_frame,
                values=[str(i) for i in range(len(self.beat_intervals))],
            )
            self.beatskip_dropdown.pack(side="top", pady=(0, 5), padx=5)

    def choose_gifs(self):
        gif_paths = filedialog.askopenfilenames()

        if gif_paths:
            self.gifs.extend(gif_paths)
            self.hot_load(gif_paths)
            self.generate_button.configure(state="normal")
        else:
            pass

    def get_pinterest_gifs(self):
        

        self.hot_load(paths)

    def generate_button_click(self):
        # 1. ask for filename
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp4", filetypes=[("MP4", "*.mp4")]
        )
        if not file_path:
            return

        # 2. deactivate button and start new thread for generation
        self.generate_button.configure(state="disabled")
        threading.Thread(target=self.generate, args=(file_path,), daemon=True).start()

    def generate(self, file_path):
        # 3. generate video
        clips = video.prepare(self.gifs)
        concatenated = video.concat_clips(
            clips, self.beat_intervals, self.duration, self.generate_clip_durations()
        )
        final_video = video.add_audio(concatenated, self.audio_path)
        final_video.write_videofile(file_path)

        # 4. set button to normal
        def on_done():
            self.generate_button.configure(state="normal")

        self.after(0, on_done)

    def generate_clip_durations(self):
        """This function isn't for setting values in dropdowns, it puts the values in a list for generation"""
        option_values = []
        for widget in self.skip_beat_frame.winfo_children():
            for stuff in widget.winfo_children():
                if not isinstance(stuff, ctk.CTkOptionMenu):
                    continue

                # skip settings drop downs
                if stuff in (
                    self.all_beatskip_dropdown,
                    self.patterns_beatskip_dropdown,
                ):
                    continue

                option_values.append(int(stuff.get()))

        return option_values

    def set_all_durations(self, duration):
        for widget in self.skip_beat_frame.winfo_children():
            for stuff in widget.winfo_children():
                if not isinstance(stuff, ctk.CTkOptionMenu):
                    continue

                # skip settings drop downs
                if stuff in (
                    self.all_beatskip_dropdown,
                    self.patterns_beatskip_dropdown,
                ):
                    continue

                stuff.set(duration)

    def set_patterns(self, option):
        option_menus = []
        # get option menus
        for widget in self.skip_beat_frame.winfo_children():
            for stuff in widget.winfo_children():
                if not isinstance(stuff, ctk.CTkOptionMenu):
                    continue

                # skip settings drop downs
                if stuff in (
                    self.all_beatskip_dropdown,
                    self.patterns_beatskip_dropdown,
                ):
                    continue

                option_menus.append(stuff)

        # get patterns out the options file we loaded at the start of App() with selected option
        self.pattern = self.data.get(option, {})

        # set pattern to option menus
        for idx, menu in enumerate(option_menus):
            val = self.pattern[idx % len(self.pattern)]
            menu.set(val)

    def get_save_pattern_name(self):
        # hide save button and dropdown and delete button to make space
        self.save_pattern_button.pack_forget()
        self.patterns_beatskip_dropdown.pack_forget()
        self.delete_pattern_button.pack_forget()

        # show entry for name
        self.pattern_name_entry.pack(side="left", anchor="n", padx=5, pady=(0, 5))
        self.final_save_button.pack(side="left", anchor="n", padx=5, pady=(0, 5))

    def save_pattern(self):
        # generate and save pattern
        pattern = self.generate_clip_durations()

        # get name from entry
        for widget in self.skip_beat_frame.winfo_children():
            for stuff in widget.winfo_children():
                if isinstance(stuff, ctk.CTkEntry):
                    name = stuff.get()

        if name:
            self.data[name] = pattern
        else:
            self.data["temp saved"] = pattern

        # write pattern in file
        with open("options/patterns.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

        # update dropdown
        current_values = list(self.patterns_beatskip_dropdown.cget("values"))
        current_values.append(name)
        self.patterns_beatskip_dropdown.configure(values=current_values)

        # hide saving things & reset entry
        self.pattern_name_entry.delete(0, "end")
        self.pattern_name_entry.pack_forget()
        self.final_save_button.pack_forget()

        # show dropdown and initial save button
        self.patterns_beatskip_dropdown.pack(
            side="left", anchor="n", padx=5, pady=(0, 5)
        )
        self.save_pattern_button.pack(side="left", anchor="n", padx=5, pady=(0, 5))
        self.delete_pattern_button.pack(side="left", anchor="n", padx=5, pady=(0, 5))

        # set dropdown to saved pattern
        self.patterns_beatskip_dropdown.set(name)

        # show message that it saved for 1 sec
        self.save_pattern_button.configure(text="Saved!")
        self.save_pattern_button.after(
            1000, lambda: self.save_pattern_button.configure(text="Save pattern")
        )

    def delete_pattern(self):
        # get pattern to delete
        name = self.patterns_beatskip_dropdown.get()

        if name in self.data:
            self.data.pop(name)

        with open("options/patterns.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

        # update dropdown
        current_values = list(self.patterns_beatskip_dropdown.cget("values"))
        current_values.append(name)
        self.patterns_beatskip_dropdown.configure(values=current_values)

        # set dropdown to default pattern
        self.patterns_beatskip_dropdown.set("default")

        # update button text
        self.delete_pattern_button.configure(text="Deleted!")
        self.delete_pattern_button.after(
            1000, lambda: self.delete_pattern_button.configure(text="Delete pattern")
        )


def main():
    audio_window = AudioDropWindow()
    audio_window.mainloop()
    audio_path = audio_window.audio_file
    tempo = audio_window.tempo
    beat_times = audio_window.beat_times
    beat_intervals = audio_window.beat_intervals
    duration = audio_window.duration
    total_gifs = audio_window.total_gifs

    # gif_window = GifDropWindow(beat_times, total_gifs)
    # gif_window.mainloop()
    # gifs = gif_window.gif_paths

    main_window = App(tempo, beat_times, beat_intervals, audio_path, duration, total_gifs)
    main_window.mainloop()

    # main_window = App(3, [], [2, 3, 54, 6], clips_path, "test_song.wav", 10)
    # main_window.mainloop()


if __name__ == "__main__":
    main()
