# Vimeo Transcript Extractor

A Streamlit-based Python application for extracting transcripts from Vimeo videos that have captions/transcripts loaded.

## Features

- Extract transcripts from any public Vimeo video with captions
- Support for multiple language tracks
- Copy transcript text directly from the interface
- Export transcripts as plain text files (.txt)
- View raw WebVTT format if needed
- Clean, user-friendly interface

## Requirements

- Python 3.8+
- Streamlit
- Requests

## Installation

1. Install dependencies:
```bash
pip install streamlit requests
```

2. Run the application:
```bash
streamlit run vimeo_transcript_extractor.py
```

3. Open your browser to the URL shown in the terminal (typically `http://localhost:8501`)

## Usage

1. Paste a Vimeo video URL into the input field
2. Click **Extract Transcript**
3. If multiple language tracks are available, select the desired one
4. View the transcript in the text area
5. Copy the text using Ctrl+C (Cmd+C on Mac) or download as a .txt file

## Supported URL Formats

- `https://vimeo.com/123456789`
- `https://vimeo.com/channels/channelname/123456789`
- `https://vimeo.com/groups/groupname/videos/123456789`
- `https://player.vimeo.com/video/123456789`

## Notes

- This tool only works with videos that have publicly accessible transcripts/captions
- Private videos or videos without captions will not work
- Some videos may require authentication or have restricted access

## License

MIT License
