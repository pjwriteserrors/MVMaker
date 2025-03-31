from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
from moviepy.video.fx.Crop import Crop

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