import re
import time
import random
import os
import io
from typing import Optional, Tuple, List, Union
import json
import tempfile
from config import settings

# YouTube Transcript API imports
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
    YOUTUBE_TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_API_AVAILABLE = False
    print("youtube-transcript-api not available. Install with: pip install youtube-transcript-api")

# yt-dlp imports
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    print("yt-dlp not available. Install with: pip install yt-dlp")

# Speech recognition imports
try:
    from pytube import YouTube
    import speech_recognition as sr
    from pydub import AudioSegment
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Speech recognition dependencies not available. Install with: pip install pytube SpeechRecognition pydub")

# Additional imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("requests not available. Install with: pip install requests")


class YouTubeTranscriptExtractor:
    """
    A comprehensive class for extracting transcripts from YouTube videos
    using multiple methods and fallback strategies.
    """
    
    def __init__(self, default_language: str = 'en', retry_count: int = 3):
        """
        Initialize the transcript extractor.
        
        Args:
            default_language: Default language code for transcripts
            retry_count: Number of retry attempts for failed requests
        """
        self.default_language = default_language
        self.retry_count = retry_count
        self.temp_files = []  # Track temp files for cleanup
    
    def extract_video_id(self, video_url: str) -> str:
        """
        Extract video ID from various YouTube URL formats.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Video ID string
            
        Raises:
            ValueError: If video ID cannot be extracted
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        
        raise ValueError("Could not extract video ID from URL")
    
    def get_transcript_youtube_api(self, video_url: str, languages: List[str] = None) -> Tuple[Optional[str], Optional[List], Optional[str]]:
        """
        Get transcript using youtube-transcript-api with robust error handling.
        
        Args:
            video_url: YouTube video URL
            languages: List of language codes to try
            
        Returns:
            Tuple of (full_text, transcript_data, transcript_type)
        """
        if not YOUTUBE_TRANSCRIPT_API_AVAILABLE:
            print("youtube-transcript-api not available")
            return None, None, None
            
        if languages is None:
            languages = [self.default_language]
            
        video_id = self.extract_video_id(video_url)
        
        for attempt in range(self.retry_count):
            try:
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    time.sleep(random.uniform(1, 3))
                    
                # Try to get manually created transcripts first
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Look for manual transcripts in preferred languages
                for language in languages:
                    try:
                        transcript = transcript_list.find_manually_created_transcript([language])
                        transcript_data = transcript.fetch()
                        full_text = ' '.join([entry['text'] for entry in transcript_data])
                        return full_text, transcript_data, 'manual'
                    except:
                        continue
                
                # Fall back to auto-generated transcripts
                for language in languages:
                    try:
                        transcript = transcript_list.find_generated_transcript([language])
                        transcript_data = transcript.fetch()
                        full_text = ' '.join([entry['text'] for entry in transcript_data])
                        return full_text, transcript_data, 'auto-generated'
                    except:
                        continue
                        
                return None, None, None
                
            except TranscriptsDisabled:
                print(f"Transcripts are disabled for video: {video_id}")
                return None, None, None
            except NoTranscriptFound:
                print(f"No transcript found for video: {video_id}")
                return None, None, None
            except VideoUnavailable:
                print(f"Video unavailable: {video_id}")
                return None, None, None
            except Exception as e:
                print(f"YouTube API attempt {attempt + 1} failed: {e}")
                if attempt == self.retry_count - 1:
                    print("All YouTube API retry attempts failed")
                    return None, None, None
                    
        return None, None, None
    
    def download_and_parse_vtt(self, subtitle_url: str) -> Optional[str]:
        """
        Download and parse VTT subtitle file.
        
        Args:
            subtitle_url: URL to VTT subtitle file
            
        Returns:
            Parsed transcript text or None
        """
        if not REQUESTS_AVAILABLE:
            print("requests library not available")
            return None
            
        try:
            response = requests.get(subtitle_url)
            response.raise_for_status()
            
            # Parse VTT content
            vtt_content = response.text
            
            # Remove VTT headers and timestamps
            lines = vtt_content.split('\n')
            text_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip empty lines, WEBVTT header, and timestamp lines
                if (line and 
                    not line.startswith('WEBVTT') and 
                    not re.match(r'^\d+$', line) and
                    not re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3}', line) and
                    not line.startswith('NOTE')):
                    # Remove HTML tags
                    clean_line = re.sub(r'<[^>]*>', '', line)
                    if clean_line:
                        text_lines.append(clean_line)
            
            return ' '.join(text_lines)
            
        except Exception as e:
            print(f"Error parsing VTT: {e}")
            return None
    
    def get_transcript_ytdlp(self, video_url: str, lang: str = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract transcript using yt-dlp - more reliable alternative.
        
        Args:
            video_url: YouTube video URL
            lang: Language code
            
        Returns:
            Tuple of (transcript_text, transcript_type)
        """
        if not YTDLP_AVAILABLE:
            print("yt-dlp not available")
            return None, None
            
        if lang is None:
            lang = self.default_language

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_cookie_file:
            tmp_cookie_file.write(settings.YT_COOKIES)
            tmp_cookie_file_path = tmp_cookie_file.name
            
        ydl_opts = {
            'cookies': tmp_cookie_file_path,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang, 'en'],
            'skip_download': True,
            'subtitlesformat': 'vtt',
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info without downloading
                info_dict = ydl.extract_info(video_url, download=False)
                
                # Check if subtitles are available
                if 'subtitles' in info_dict and info_dict['subtitles']:
                    # Try manual subtitles first
                    for lang_code in [lang, 'en']:
                        if lang_code in info_dict['subtitles']:
                            subtitle_url = info_dict['subtitles'][lang_code][0]['url']
                            transcript_text = self.download_and_parse_vtt(subtitle_url)
                            caption_data = json.loads(transcript_text)
                            transcript_text = self._parse_caption_json(caption_data)
                            if transcript_text:
                                return transcript_text, 'manual'
                
                # Try automatic subtitles
                if 'automatic_captions' in info_dict and info_dict['automatic_captions']:
                    for lang_code in [lang, 'en']:
                        if lang_code in info_dict['automatic_captions']:
                            subtitle_url = info_dict['automatic_captions'][lang_code][0]['url']
                            transcript_text = self.download_and_parse_vtt(subtitle_url)
                            caption_data = json.loads(transcript_text)
                            transcript_text = self._parse_caption_json(caption_data)
                            if transcript_text:
                                return transcript_text, 'auto-generated'
                
                return None, None
                
        except Exception as e:
            print(f"Error with yt-dlp method: {e}")
            return None, None
    
    def _parse_caption_json(self, caption_data: dict) -> str:
        """Convert caption JSON (YouTube .json3 format) into a readable transcript."""
        transcript = []
        current_line = ""

        for event in caption_data.get("events", []):
            segs = event.get("segs")
            if not segs:
                continue
            for seg in segs:
                text = seg.get("utf8", "")
                if text == "\n":
                    if current_line.strip():
                        transcript.append(current_line.strip())
                        current_line = ""
                else:
                    current_line += text

        if current_line.strip():
            transcript.append(current_line.strip())

        return " ".join(transcript)
    
    def transcribe_with_speech_recognition(self, video_url: str) -> Optional[str]:
        """
        Use pytube + speech_recognition for transcription.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Transcript text or None
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("Speech recognition dependencies not available")
            return None
            
        try:
            # Download audio stream
            yt = YouTube(video_url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            # Download to memory
            buffer = io.BytesIO()
            audio_stream.stream_to_buffer(buffer)
            buffer.seek(0)
            
            # Convert to WAV
            audio = AudioSegment.from_file(buffer)
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            
            # Transcribe
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_buffer) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                
            return text
            
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None
    
    def save_transcript(self, transcript: Union[str, List], filename: str) -> bool:
        """
        Save transcript to file.
        
        Args:
            transcript: Transcript text or list of transcript entries
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(transcript, str):
                    f.write(transcript)
                elif isinstance(transcript, list):
                    for entry in transcript:
                        if isinstance(entry, dict) and 'text' in entry:
                            f.write(f"{entry.get('start', 0):.2f}s: {entry['text']}\n")
                        else:
                            f.write(str(entry) + '\n')
            return True
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return False
    
    def get_transcript(self, video_url: str, languages: List[str] = None, 
                    use_whisper: bool = False, whisper_model: str = 'base') -> Tuple[Optional[str], Optional[str]]:
        """
        Get transcript using all available methods with fallback strategy.
        
        Args:
            video_url: YouTube video URL
            languages: List of language codes to try
            use_whisper: Whether to use Whisper as fallback
            whisper_model: Whisper model size
            
        Returns:
            Tuple of (transcript_text, method_used)
        """
        if languages is None:
            languages = [self.default_language]
            
        print("Attempting transcript extraction...")
        
        # Method 1: YouTube Transcript API
        print("Trying Method 1: YouTube Transcript API...")
        text, transcript_data, transcript_type = self.get_transcript_youtube_api(video_url, languages)
        
        if text:
            print(f"✓ Found {transcript_type} transcript with YouTube API!")
            return text, f"youtube_api_{transcript_type}"
        
        # Method 2: yt-dlp caption extraction
        print("Trying Method 2: yt-dlp caption extraction...")
        ytdlp_text, ytdlp_type = self.get_transcript_ytdlp(video_url, languages[0])
        
        if ytdlp_text:
            print(f"✓ Found {ytdlp_type} transcript with yt-dlp!")
            return ytdlp_text, f"ytdlp_{ytdlp_type}"
        
        # Method 4: Speech recognition (last resort)
        print("Trying Method 4: Speech recognition...")
        sr_text = self.transcribe_with_speech_recognition(video_url)
        
        if sr_text:
            print("✓ Speech recognition successful!")
            return sr_text, "speech_recognition"
        
        print("✗ All transcription methods failed")
        return None, None
    
    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error cleaning up {temp_file}: {e}")
        self.temp_files.clear()
    
    def __del__(self):
        """Destructor to clean up temporary files."""
        self.cleanup()
