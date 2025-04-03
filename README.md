# Dialogger

A Python application that converts audio files containing speech into SubRip Subtitle (SRT) format files. I designed this app to decode dialogue stems from a feature into SRT subtitle files. I do recommend running this through another app such as Subtitle Edit to clean up and small issues.

## Requirements

- Python 3.6 or higher
- FFmpeg (required for audio processing)
- CUDA-capable GPU (optional, but recommended for faster processing)

## Installation

1. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python dialogger.py
```

This will open a user-friendly interface where you can:
- Select your input audio file using the "Browse" button
- Choose where to save the output SRT file
- Select the Whisper model size (tiny, base, small, medium, or large)
- Choose the processing device (CPU or CUDA GPU)
- Preview the generated subtitles in real-time
- Click "Convert to SRT" to start the conversion

## Features

- Supports various audio formats (mp3, wav, m4a, etc.)
- Uses OpenAI's Whisper for highly accurate speech recognition
- Generates sentence-level SRT subtitles with precise timestamps
- Automatically handles audio format conversion
- User-friendly GUI interface with progress indication
- File selection dialogs for easy file browsing
- Multiple model size options for different accuracy/speed trade-offs
- GPU acceleration support for faster processing
- Real-time subtitle preview
- Progress bar for conversion status
- Threaded processing to keep the interface responsive

## Notes

- The first time you run the application, it will automatically download the selected Whisper model
- Model sizes and their characteristics:
  - tiny: Fastest, least accurate
  - base: Good balance of speed and accuracy
  - small: Better accuracy, slower
  - medium: High accuracy, slower
  - large: Best accuracy, slowest
- For best results, use clear audio with minimal background noise
- GPU processing is significantly faster than CPU processing
- The preview window shows the first 5 segments of the generated subtitles 