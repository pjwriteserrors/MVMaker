import librosa
import numpy as np

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