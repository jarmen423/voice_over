import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox




def is_wsl():
    """Check if running in WSL."""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def ask_file(title, filetypes):
    """Ask for a file using native Windows dialog if in WSL, else Tkinter."""
    if is_wsl():
        return ask_file_wsl(title, filetypes)
    else:
        root = tk.Tk()
        root.withdraw()
        return filedialog.askopenfilename(title=title, filetypes=filetypes)


def show_message(title, message):
    """Show message using native Windows dialog if in WSL, else Tkinter."""
    if is_wsl():
        # Escape single quotes for PowerShell
        safe_msg = message.replace("'", "''")
        safe_title = title.replace("'", "''")
        cmd = [
            "powershell.exe", "-NoProfile", "-Command",
            f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('{safe_msg}', '{safe_title}')"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        messagebox.showinfo(title, message)


def ask_file_wsl(title, filetypes):
    """Use PowerShell to open a Windows native file dialog."""
    # Convert filetypes [("Name", "*.ext")] -> "Name (*.ext)|*.ext"
    filter_parts = []
    for name, pattern in filetypes:
        filter_parts.append(f"{name} ({pattern})|{pattern}")
    filter_str = "|".join(filter_parts)

    ps_cmd = [
        "powershell.exe", "-NoProfile", "-Command",
        "Add-Type -AssemblyName System.Windows.Forms;",
        "$f = New-Object System.Windows.Forms.OpenFileDialog;",
        f"$f.Filter = '{filter_str}';",
        f"$f.Title = '{title}';",
        "if ($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $f.FileName }"
    ]
    
    try:
        # Run PowerShell to get the Windows path
        result = subprocess.run(
            ps_cmd,
            capture_output=True,
            text=True
        )
        win_path = result.stdout.strip()

        if not win_path:
            return ""

        # Convert Windows path to WSL path
        wsl_path = subprocess.run(
            ["wslpath", "-u", win_path],
            capture_output=True,
            text=True
        ).stdout.strip()
        return wsl_path
    
    except Exception as e:
        print(f"Error invoking Windows dialog: {e}")
        return ""


def merge_with_video(video_path, audio_path):
    """Merge the generated audio with the original video file."""
    # Determine output path based on video path
    output_video = os.path.splitext(video_path)[0] + "_COMPLETED.mp4"
    
    print(f"Merging {audio_path} into {video_path}...")

    # Run FFMPEG command via Python
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
    show_message("Done!", f"Video created:\n{output_video}")


def main():
    """Main entry point - prompts user to select Video and audio files."""
    # Select Video file
    video_path = ask_file(
        title="Select Original Video File (.mp4)",
        filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
    )
    if not video_path:
        return
    
    # Select the generated audio file
    audio_path = ask_file(
        title="Select the Generated Audio File (.mp3)",
        filetypes=[("MP3 Files", "*.mp3"), ("All Files", "*.*")]
    )
    if not audio_path:
        return
    
    merge_with_video(video_path, audio_path)


if __name__ == "__main__":
    main()
