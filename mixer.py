import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment


def mix_audio(voice_path, music_path=None):
    """Mix background music under a voiceover track.
    
    Args:
        voice_path: Path to the voiceover audio file
        music_path: Optional path to music file. If None, will prompt user to select.
    
    Returns:
        Path to the mixed audio file, or None if cancelled.
    """
    root = tk.Tk()
    root.withdraw()

    # Select music if not provided
    if not music_path:
        music_path = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=[("Audio", "*.mp3 *.wav")]
        )
        if not music_path:
            return None

    print(f"Mixing {os.path.basename(music_path)} under voice...")
    
    voice = AudioSegment.from_file(voice_path)
    music = AudioSegment.from_file(music_path)
    
    # LOOP MUSIC
    target_duration = len(voice)
    while len(music) < target_duration:
        music += music

    # TRIM & FADE
    music = music[:target_duration + 3000]  # Add 3s tail
    music = music - 22  # Ducking (-22dB)
    music = music.fade_out(3000)

    # OVERLAY
    final_mix = music.overlay(voice)
    
    output_path = voice_path.replace(".mp3", "_MIXED.mp3")
    if output_path == voice_path: 
        output_path = voice_path.replace(".mp3", "_FINAL_MIX.mp3")

    final_mix.export(output_path, format="mp3")
    messagebox.showinfo("Success", f"Mixed audio saved to:\n{output_path}")
    
    return output_path


def run_mixer():
    """Standalone entry point - prompts user to select both files."""
    root = tk.Tk()
    root.withdraw()

    # 1. SELECT VOICEOVER
    voice_path = filedialog.askopenfilename(
        title="Select Voiceover File (.mp3)",
        filetypes=[("Audio", "*.mp3 *.wav")]
    )
    if not voice_path:
        return

    mix_audio(voice_path)


if __name__ == "__main__":
    run_mixer()