from modules import audio, video

audio_path = "test_song.wav"
clips_path = [
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl2.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl3.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl4.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl5.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl6.gif",
    "/mnt/EDrive/Music/Adobe/Premiere/Other-Videos/Pinterest/aestheticgirl7.gif"
]

tempo, beat_times, beat_intervals = audio.get_intervals(audio_path)
clips = video.prepare(clips_path)
concatenated_video = video.concat_clips(clips, beat_intervals)
final_video = video.add_audio(concatenated_video, audio_path)

final_video.write_videofile("test.mp4")
