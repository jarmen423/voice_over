import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


def merge_with_video(srt_path, audio_path):
    """Merge the generated audio with the original video file."""
    # 1. Guess video path (assumes same filename as SRT, but .mp4)
    video_path = srt_path.replace(".srt", ".mp4")
    
    # 2. If guessed path doesn't exist, ask user to pick it
    if not os.path.exists(video_path):
        root = tk.Tk()
        root.withdraw()
        video_path = filedialog.askopenfilename(
            title="Select Original Video File (.mp4)",
            filetypes=[("MP4 Files", "*.mp4")]
        )
        if not video_path:
            return

    output_video = srt_path.replace(".srt", "_COMPLETED.mp4")
    print(f"Merging {audio_path} into {video_path}...")

    # 3. Run FFMPEG command via Python
    cmd = [
        "ffmpeg", "-y",                 # Overwrite without asking
        "-i", video_path,               # Input Video
        "-i", audio_path,               # Input Audio (New Voiceover)
        "-c:v", "copy",                 # Copy video stream (no re-encoding, fast)
        "-map", "0:v", "-map", "1:a",   # Map Video from 0, Audio from 1
        "-shortest",                    # Stop when the shortest stream ends
        output_video
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    messagebox.showinfo("Done!", f"Video created:\n{output_video}")


def main():
    """Main entry point - prompts user to select SRT and audio files."""
    root = tk.Tk()
    root.withdraw()
    
    # Select SRT file (used to determine output name and guess video path)
    srt_path = filedialog.askopenfilename(
        title="Select your Subtitle File (.srt)",
        filetypes=[("Subtitle Files", "*.srt"), ("All Files", "*.*")]
    )
    if not srt_path:
        return
    
    # Select the generated audio file
    audio_path = filedialog.askopenfilename(
        title="Select the Generated Audio File (.mp3)",
        filetypes=[("MP3 Files", "*.mp3"), ("All Files", "*.*")]
    )
    if not audio_path:
        return
    
    merge_with_video(srt_path, audio_path)


if __name__ == "__main__":
    main()
