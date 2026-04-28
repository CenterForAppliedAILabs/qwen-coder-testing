import streamlit as st
import requests
import re
import json

st.set_page_config(
    page_title="Vimeo Transcript Extractor",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Vimeo Transcript Extractor")
st.markdown("""
Extract transcripts from Vimeo videos that have captions/transcripts loaded.
Simply paste the Vimeo video URL and click **Extract Transcript**.
""")

def extract_video_id(url):
    """Extract Vimeo video ID from various URL formats."""
    patterns = [
        r'vimeo\.com/(\d+)',
        r'vimeo\.com/channels/\w+/(\d+)',
        r'vimeo\.com/groups/\w+/videos/(\d+)',
        r'player\.vimeo\.com/video/(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_vimeo_player_config(video_id):
    """Fetch the player configuration JSON from Vimeo which contains transcript info."""
    try:
        # First, get the video page to find the config URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(f'https://vimeo.com/{video_id}', headers=headers, timeout=15)
        response.raise_for_status()
        
        # Look for the config URL in the page
        config_match = re.search(r'data-config-url="([^"]+)"', response.text)
        if not config_match:
            # Try alternative pattern
            config_match = re.search(r'"config_url":"([^"]+)"', response.text)
        
        if config_match:
            config_url = config_match.group(1).replace('&amp;', '&')
            config_response = requests.get(config_url, headers=headers, timeout=15)
            config_response.raise_for_status()
            return config_response.json()
        
        # Alternative: look for embedded config JSON
        config_json_match = re.search(r'vp\s*=\s*({.+?});', response.text)
        if config_json_match:
            return json.loads(config_json_match.group(1))
            
        return None
        
    except Exception as e:
        st.error(f"Error fetching video config: {str(e)}")
        return None

def extract_transcript_from_config(config):
    """Extract transcript data from Vimeo player config."""
    if not config:
        return None
    
    try:
        # Look for text tracks in the config
        request_data = config.get('request', {})
        text_tracks = request_data.get('textTracks', [])
        
        if text_tracks:
            return text_tracks
        
        # Also check in config directly
        text_tracks = config.get('textTracks', [])
        if text_tracks:
            return text_tracks
            
        return None
        
    except Exception as e:
        st.error(f"Error parsing config: {str(e)}")
        return None

def fetch_transcript_content(track_url):
    """Fetch the actual transcript content from the track URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        response = requests.get(track_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Vimeo transcripts are typically in WebVTT format
        return response.text
        
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

def parse_webvtt(webvtt_content):
    """Parse WebVTT content and extract plain text."""
    if not webvtt_content:
        return ""
    
    lines = webvtt_content.split('\n')
    text_lines = []
    
    for line in lines:
        # Skip WEBVTT header, timestamps, and empty lines
        if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'):
            continue
        if '-->' in line:
            continue
        if line.strip() == '' or line.strip().isdigit():
            continue
        # Remove HTML tags if present
        clean_line = re.sub(r'<[^>]+>', '', line)
        if clean_line.strip():
            text_lines.append(clean_line.strip())
    
    return '\n'.join(text_lines)

# Main app
video_url = st.text_input(
    "Enter Vimeo Video URL:",
    placeholder="https://vimeo.com/123456789",
    help="Paste the full Vimeo video URL here"
)

if video_url:
    video_id = extract_video_id(video_url)
    
    if not video_id:
        st.error("Invalid Vimeo URL. Please check the URL and try again.")
    else:
        st.success(f"Video ID detected: {video_id}")
        
        if st.button("🔍 Extract Transcript", type="primary"):
            with st.spinner("Fetching video information..."):
                config = get_vimeo_player_config(video_id)
                
                if config:
                    text_tracks = extract_transcript_from_config(config)
                    
                    if text_tracks:
                        st.success(f"Found {len(text_tracks)} transcript track(s)!")
                        
                        # Display available tracks
                        track_options = {}
                        for i, track in enumerate(text_tracks):
                            lang = track.get('lang', 'Unknown')
                            kind = track.get('kind', 'captions')
                            name = f"{lang} ({kind})"
                            track_url = track.get('url', '')
                            track_options[name] = track_url
                        
                        selected_track = st.selectbox(
                            "Select transcript language:",
                            options=list(track_options.keys())
                        )
                        
                        if selected_track:
                            track_url = track_options[selected_track]
                            
                            with st.spinner("Downloading transcript..."):
                                webvtt_content = fetch_transcript_content(track_url)
                                
                                if webvtt_content:
                                    plain_text = parse_webvtt(webvtt_content)
                                    
                                    st.subheader("📄 Transcript Preview")
                                    st.text_area(
                                        "Transcript Content",
                                        value=plain_text,
                                        height=400,
                                        key="transcript_display"
                                    )
                                    
                                    # Copy button (using Streamlit's built-in copy via text_area)
                                    st.info("💡 To copy: Select the text in the box above and use Ctrl+C (Cmd+C on Mac)")
                                    
                                    # Export to file
                                    st.download_button(
                                        label="📥 Download Transcript (.txt)",
                                        data=plain_text,
                                        file_name=f"vimeo_{video_id}_transcript.txt",
                                        mime="text/plain"
                                    )
                                    
                                    # Also show raw WebVTT option
                                    with st.expander("Show Raw WebVTT Format"):
                                        st.code(webvtt_content, language="webvtt")
                                        
                    else:
                        st.warning("""
                        ⚠️ No transcript found for this video.
                        
                        This could mean:
                        - The video doesn't have captions/transcripts enabled
                        - The video is private or password-protected
                        - The transcript is not publicly accessible
                        
                        Make sure the video has publicly available captions.
                        """)
                else:
                    st.error("""
                    Could not retrieve video configuration.
                    
                    Possible reasons:
                    - The video is private or requires authentication
                    - The video URL is incorrect
                    - Vimeo blocked the request (try again later)
                    """)

st.markdown("---")
st.markdown("""
**Note:** This tool only works with Vimeo videos that have publicly accessible transcripts/captions. 
Private videos or videos without captions will not work.
""")
