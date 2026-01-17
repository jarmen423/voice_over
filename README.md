# 🎙️ Voice Over Generator

An AI-powered voiceover generation pipeline that converts subtitle files (.srt) into expressive, natural-sounding audio using **ElevenLabs** and **xAI Grok**.

## ✨ Features

- **AI-Enhanced Dialogue** — Uses Grok to add expressive audio tags (`[excited]`, `[sighs]`, etc.) for natural delivery
- **ElevenLabs v3** — Generates high-quality speech with full audio tag support
- **Timeline Sync** — Audio is precisely synced to your subtitle timestamps
- **Background Music Mixer** — Optional ducked background music with auto-loop and fade
- **Video Merge** — Automatically combine audio with your original video (no re-encoding)

## 📁 Project Structure

```
voice_over/
├── voice_over.py      # Main script - generates voiceover from SRT
├── mixer.py           # Mix background music under voiceover
├── merge_video.py     # Merge audio with video using ffmpeg
└── .env               # API keys (not tracked in git)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install elevenlabs pydub pysrt openai python-dotenv
```

You'll also need **ffmpeg** installed on your system:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### 2. Set Up API Keys

Create a `.env` file in the project root:

```env
ELEVEN_API_KEY=your_elevenlabs_api_key
XAI_API_KEY=your_xai_api_key
VOICE_ID=your_elevenlabs_voice_id
```

Or leave the `.env` empty — the script will prompt you for keys on each run.

### 3. Run the Pipeline

```bash
python voice_over.py
```

You'll be prompted to:
1. Select your `.srt` subtitle file
2. After generation: **Add background music?** (optional)
3. After that: **Merge with video?** (optional)

## 🎛️ Standalone Scripts

Each module can be run independently:

| Script | Command | Description |
|--------|---------|-------------|
| **voice_over.py** | `python voice_over.py` | Full pipeline: SRT → Audio |
| **mixer.py** | `python mixer.py` | Add background music to any audio |
| **merge_video.py** | `python merge_video.py` | Combine audio + video with ffmpeg |

## 📝 Workflow Examples

### Full Automated Pipeline
```bash
python voice_over.py
# → Select SRT
# → Yes to music
# → Yes to video
# → Output: video_COMPLETED.mp4
```

### Generate, Review, Then Decide
```bash
python voice_over.py    # Say No to both prompts
# Listen to _FINAL_TAGGED.mp3
python mixer.py         # Add music if you like it
python merge_video.py   # Create final video
```

## 🎚️ Configuration

### ElevenLabs Voice Settings

In `voice_over.py`, you can adjust these settings:

```python
voice_settings=VoiceSettings(
    stability=0.0,        # 0.0 = Max expressiveness, 1.0 = Consistent
    similarity_boost=0.8, # Voice similarity to original
    style=0.0,            # 0.0 = Natural, 1.0 = Exaggerated
    use_speaker_boost=True
)
```

### Music Mixer Settings

In `mixer.py`:
- **Ducking**: `-22dB` (music volume under voice)
- **Tail**: `3 seconds` extra at the end
- **Fade out**: `3 seconds`

## 📄 Output Files

| Input | Output |
|-------|--------|
| `video.srt` | `video_FINAL_TAGGED.mp3` (voiceover) |
| + background music | `video_FINAL_TAGGED_MIXED.mp3` |
| + original video | `video_COMPLETED.mp4` |

## 🔧 Troubleshooting

### "No module named 'elevenlabs'"
```bash
pip install elevenlabs
```

### "ffmpeg not found"
Make sure ffmpeg is installed and in your system PATH.

### Audio overlaps in output
Check your `.srt` file timing — each subtitle should have enough duration for the text. Longer sentences need more time (aim for ~150 words/minute).

## 📜 License

MIT License — use freely for personal and commercial projects.