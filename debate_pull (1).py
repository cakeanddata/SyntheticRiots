#!/usr/bin/env python3
"""
YouTube Debate Transcript Puller and Location Analyzer
Extracts transcript from YouTube video and analyzes location mentions
"""

import re
import json
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
from pathlib import Path

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    # Handle different YouTube URL formats
    parsed_url = urlparse(url)
    
    if 'youtube.com' in parsed_url.netloc:
        if '/watch' in parsed_url.path:
            # Regular YouTube URL
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        elif '/live' in parsed_url.path:
            # YouTube Live URL
            video_id = parsed_url.path.split('/')[-1]
            # Remove any query parameters
            video_id = video_id.split('?')[0]
            return video_id
    elif 'youtu.be' in parsed_url.netloc:
        # Short YouTube URL
        return parsed_url.path[1:]
    
    return None

def get_transcript(video_url, start_time="4:14:00", end_time="6:04:24"):
    """Download and process transcript from YouTube video for specific time segment
    
    Args:
        video_url: YouTube video URL
        start_time: Start time in HH:MM:SS or MM:SS format
        end_time: End time in HH:MM:SS or MM:SS format
    """
    video_id = extract_video_id(video_url)
    
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {video_url}")
    
    print(f"Extracting transcript for video ID: {video_id}")
    print(f"Time segment: {start_time} to {end_time}")
    
    # Convert time strings to seconds
    def time_to_seconds(time_str):
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return int(parts[0])
    
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    
    print(f"Extracting segment from {start_seconds}s to {end_seconds}s")
    
    try:
        # Try to get transcript in English
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-GB', 'en-US'])
    except Exception as e:
        print(f"Error getting transcript: {e}")
        # Try auto-generated captions as fallback
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(transcript)
    
    # Filter for the specific time segment
    df_segment = df[(df['start'] >= start_seconds) & (df['start'] <= end_seconds)].copy()
    
    print(f"Found {len(df_segment)} transcript segments in time range")
    
    if len(df_segment) == 0:
        print("WARNING: No transcript found in specified time range!")
        print(f"Transcript starts at {df['start'].min()}s and ends at {df['start'].max()}s")
        return "", df_segment
    
    # Create both raw and cleaned versions from the segment
    segment_text = " ".join(df_segment["text"])
    
    # Save raw transcript segment
    with open("debate_transcript_raw.txt", "w", encoding="utf-8") as f:
        f.write(segment_text)
    
    # Clean the text
    cleaned_text = clean_transcript(segment_text)
    
    # Save cleaned transcript
    with open("debate_transcript_clean.txt", "w", encoding="utf-8") as f:
        f.write(cleaned_text)
    
    print(f"✅ Saved transcript segment ({start_time} to {end_time}):")
    print(f"   - debate_transcript_raw.txt ({len(segment_text.split())} words)")
    print(f"   - debate_transcript_clean.txt ({len(cleaned_text.split())} words)")
    
    # Also save DataFrame with timestamps for potential future use
    df_segment.to_csv("debate_transcript_timestamps.csv", index=False)
    
    # Calculate segment duration
    duration_seconds = end_seconds - start_seconds
    duration_minutes = duration_seconds / 60
    print(f"   - Segment duration: {duration_minutes:.1f} minutes")
    
    return cleaned_text, df_segment

def clean_transcript(text):
    """Clean transcript text by removing timestamps, brackets, and normalizing whitespace"""
    # Remove timestamps (various formats)
    text = re.sub(r'\d{1,2}:\d{2}(:\d{2})?', '', text)
    
    # Remove content in square brackets (usually [Applause], [Music], etc.)
    text = re.sub(r'\[.*?\]', '', text)
    
    # Remove content in parentheses that looks like stage directions
    text = re.sub(r'\([Aa]pplause\)', '', text)
    text = re.sub(r'\([Ll]aughter\)', '', text)
    text = re.sub(r'\([Mm]usic\)', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def main():
    # The specific debate video URL
    VIDEO_URL = "https://www.youtube.com/live/dV3nv1MclzA?si=xG0j04ZfJDEZmdfo"
    
    # Extract only the debate segment from 4:14:00 to 6:04:24
    START_TIME = "4:14:00"  # 4 hours 14 minutes
    END_TIME = "6:04:24"    # 6 hours 4 minutes 24 seconds
    
    print(f"Processing video: {VIDEO_URL}")
    print(f"Extracting segment: {START_TIME} to {END_TIME}")
    
    try:
        cleaned_text, df = get_transcript(VIDEO_URL, START_TIME, END_TIME)
        
        if len(df) > 0:
            # Save metadata
            metadata = {
                "video_url": VIDEO_URL,
                "video_id": extract_video_id(VIDEO_URL),
                "segment_start": START_TIME,
                "segment_end": END_TIME,
                "segment_start_seconds": df['start'].min() if len(df) > 0 else 0,
                "segment_end_seconds": df['start'].max() + df['duration'].iloc[-1] if len(df) > 0 else 0,
                "segment_duration_seconds": (df['start'].max() + df['duration'].iloc[-1] - df['start'].min()) if len(df) > 0 else 0,
                "total_segments": len(df),
                "total_words": len(cleaned_text.split())
            }
            
            with open("debate_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Saved metadata to debate_metadata.json")
            
            return cleaned_text
        else:
            print("⚠️ No transcript found in specified time range")
            return None
        
    except Exception as e:
        print(f"Error processing video: {e}")
        return None

if __name__ == "__main__":
    main()
