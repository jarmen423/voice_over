import os
import io
import pysrt
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- 1. FULL SYSTEM PROMPT (VERBATIM FROM enhance_prompt.md) ---
SYSTEM_PROMPT = """# Instructions

## 1. Role and Goal

You are an AI assistant specializing in enhancing dialogue text for speech generation.

Your **PRIMARY GOAL** is to dynamically integrate **audio tags** (e.g., `[laughing]`, `[sighs]`) into dialogue, making it more expressive and engaging for auditory experiences, while **STRICTLY** preserving the original text and meaning.

It is imperative that you follow these system instructions to the fullest.

## 2. Core Directives

Follow these directives meticulously to ensure high-quality output.

### Positive Imperatives (DO):

* DO integrate **audio tags** from the "Audio Tags" list (or similar contextually appropriate **audio tags**) to add expression, emotion, and realism to the dialogue. These tags MUST describe something auditory.
* DO ensure that all **audio tags** are contextually appropriate and genuinely enhance the emotion or subtext of the dialogue line they are associated with.
* DO strive for a diverse range of emotional expressions (e.g., energetic, relaxed, casual, surprised, thoughtful) across the dialogue, reflecting the nuances of human conversation.
* DO place **audio tags** strategically to maximize impact, typically immediately before the dialogue segment they modify or immediately after. (e.g., `[annoyed] This is hard.` or `This is hard. [sighs]`).
* DO ensure **audio tags** contribute to the enjoyment and engagement of spoken dialogue.
* **CRITICAL:** Ensure tags are strictly formatted as `[tag]`. Do not use parentheses `(tag)` or other formats, as the TTS engine might read those aloud.


### Negative Imperatives (DO NOT):

* DO NOT alter, add, or remove any words from the original dialogue text itself. Your role is to *prepend* **audio tags**, not to *edit* the speech. **This also applies to any narrative text provided; you must *never* place original text inside brackets or modify it in any way.**
* DO NOT create **audio tags** from existing narrative descriptions. **Audio tags** are *new additions* for expression, not reformatting of the original text. (e.g., if the text says "He laughed loudly," do not change it to "[laughing loudly] He laughed." Instead, add a tag if appropriate, e.g., "He laughed loudly [chuckles].")
* DO NOT invent new dialogue lines.
* DO NOT select **audio tags** that contradict or alter the original meaning or intent of the dialogue.
* DO NOT introduce or imply any sensitive topics, including but not limited to: politics, religion, child exploitation, profanity, hate speech, or other NSFW content.

**Note:** With ElevenLabs v3 alpha, you now have access to FULL audio tag support including emotions, delivery styles, human reactions, and descriptive expression tags. Feel free to experiment with any contextually appropriate audio tags.

## 3. Workflow

1. **Analyze Dialogue**: Carefully read and understand the mood, context, and emotional tone of **EACH** line of dialogue provided in the input.
2. **Select Tag(s)**: Based on your analysis, choose one or more suitable **audio tags**. Ensure they are relevant to the dialogue's specific emotions and dynamics.
3. **Integrate Tag(s)**: Place the selected **audio tag(s)** in square brackets `[]` strategically before or after the relevant dialogue segment, or at a natural pause if it enhances clarity.
4. **Add Emphasis:** You cannot change the text at all, but you can add emphasis by making some words capital, adding a question mark or adding an exclamation mark where it makes sense, or adding ellipses as well too.
5. **Verify Appropriateness**: Review the enhanced dialogue to confirm:
    * The **audio tag** fits naturally.
    * It enhances meaning without altering it.
    * It adheres to all Core Directives.

## 4. Output Format

* Present ONLY the enhanced dialogue text in a conversational format.
* **Audio tags** **MUST** be enclosed in square brackets (e.g., `[laughing]`).
* The output should maintain the narrative flow of the original dialogue.

## 5. Audio Tags (Non-Exhaustive)

Use these as a guide. You can infer similar, contextually appropriate **audio tags**.

**Emotional Directions:**
* `[happy]`
* `[sad]`
* `[excited]`
* `[angry]`
* `[annoyed]`
* `[appalled]`
* `[thoughtful]`
* `[surprised]`
* `[curious]`
* `[mischievously]`
* `[nervous]`
* `[confident]`
* `[scared]`
* `[proud]`
* *(and similar emotional/delivery directions)*

**Delivery Styles:**
* `[whisper]`
* `[whispering]`
* `[shouts]`
* `[shouting]`
* `[singing]`
* `[muttering]`
* `[sarcastically]`
* *(and similar delivery styles)*

**Non-verbal Sounds:**
* `[laughing]`
* `[laughs]`
* `[chuckles]`
* `[giggles]`
* `[sighs]`
* `[clears throat]`
* `[short pause]`
* `[long pause]`
* `[exhales sharply]`
* `[inhales deeply]`
* `[gasps]`
* `[coughs]`
* `[yawns]`
* *(and similar non-verbal sounds)*
"""

# --- 2. CONFIGURATION & HELPERS ---

def get_user_input(prompt_title, prompt_text):
    """Pop-up dialog to get input from user without using .env"""
    root = tk.Tk()
    root.withdraw() # Hide main window
    user_input = simpledialog.askstring(prompt_title, prompt_text)
    return user_input

def get_file_path():
    """Pop-up dialog to select file"""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select your Subtitle File (.srt)",
        filetypes=[("Subtitle Files", "*.srt"), ("All Files", "*.*")]
    )
    return file_path

def optimize_text_with_grok(client, raw_text):
    """Sends text to xAI for tagging"""
    try:
        # Note: Using 'grok-beta' as the reliable endpoint. 
        # If 'grok-4-1-fast-reasoning' is available to your account, change the string below.
        response = client.chat.completions.create(
            model="grok-4-1-fast-reasoning", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Enhance this line: \"{raw_text}\""}
            ],
            temperature=0.3
        )
        optimized_text = response.choices[0].message.content.strip()
        
        # Clean quotes if the LLM adds them unnecessarily
        if optimized_text.startswith('"') and optimized_text.endswith('"'):
            optimized_text = optimized_text[1:-1]
            
        print(f"   [Grok]: {optimized_text}")
        return optimized_text
    except Exception as e:
        print(f"   [Error]: {e}. Using original text.")
        return raw_text

def main():
    eleven_key = os.getenv("ELEVEN_API_KEY")
    if not eleven_key:
        eleven_key = get_user_input("ElevenLabs API", "Enter your ElevenLabs API Key:")
        if not eleven_key: return

    xai_key = os.getenv("XAI_API_KEY")
    if not xai_key:
        xai_key = get_user_input("xAI API", "Enter your xAI API Key:")
        if not xai_key: return
    voice_id = os.getenv("VOICE_ID")
    if not voice_id:
        voice_id = get_user_input("Voice Selection", "Enter the ElevenLabs Voice ID:")
        if not voice_id: return

    # B. INITIALIZE CLIENTS
    try:
        el_client = ElevenLabs(api_key=eleven_key)
        xai_client = OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1")
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))
        return

    # C. SELECT FILE
    input_srt = get_file_path()
    if not input_srt: return

    print(f"Processing: {input_srt}")
    subs = pysrt.open(input_srt)
    
    # D. SETUP AUDIO CANVAS
    # Calculate total duration from the last subtitle's end timestamp + 2 seconds buffer
    total_duration = subs[-1].end.ordinal + 2000
    final_track = AudioSegment.silent(duration=total_duration)

    # E. PROCESS LOOP
    print("\n--- Starting Generation ---")
    for index, sub in enumerate(subs):
        original_text = sub.text.replace("\n", " ")
        
        # Manual Override for Name pronunciation (LLM might miss it if not explicit in prompt)
        original_text = original_text.replace("Malik neighbors", "Malik Nabers")

        if not original_text.strip(): continue

        print(f"Line {index+1}: {original_text}")
        
        # 1. Grok Optimization
        final_text = optimize_text_with_grok(xai_client, original_text)

        # 2. ElevenLabs Generation
        try:
            audio_stream = el_client.text_to_speech.convert(
                text=final_text,
                voice_id=voice_id,
                model_id="eleven_v3",
                voice_settings=VoiceSettings(
                    stability=0.5,       # Lower = More emotion
                    similarity_boost=0.8, 
                    style=0.6,           # Higher = More exaggeration
                    use_speaker_boost=True
                )
            )
            
            audio_data = b"".join(audio_stream)
            segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
            
            # 3. Sync to Timeline (Exact overlay)
            final_track = final_track.overlay(segment, position=sub.start.ordinal)
            
        except Exception as e:
            print(f"   [Gen Error]: {e}")

    # F. EXPORT
    output_path = input_srt.replace(".srt", "_FINAL_TAGGED.mp3")
    final_track.export(output_path, format="mp3")
    
    print(f"Done! Saved to {output_path}")
    messagebox.showinfo("Complete", f"Audio saved to:\n{output_path}")
    
    # G. OPTIONAL: MERGE WITH VIDEO
    root = tk.Tk()
    root.withdraw()
    if messagebox.askyesno("Merge with Video?", "Do you want to merge this audio with the original video?"):
        from merge_video import merge_with_video
        merge_with_video(input_srt, output_path)

if __name__ == "__main__":
    main()
