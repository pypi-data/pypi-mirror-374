"""Video indexing module for zapdos."""

import os
import tempfile
import av
import cv2
import aiofiles
import queue
import threading
import asyncio
import requests
import jsonlines
import json
from pathlib import Path
from multiprocessing import cpu_count, get_context
from typing import List, Union, Tuple, Callable, Optional
from .video_indexer_utils import (
    _upload_and_index_frames,
)

from .extract_frames import (
    _encode_frame,
    _write_file_async,
    _background_writer,
    _process_chunk,
    extract_keyframes,
)

def index(video_path: Union[str, Path], interval_sec: int = 30, server_url: str = "https://api.zapdoslabs.com", 
          progress_callback: Optional[Callable[[dict], None]] = None, api_key: Optional[str] = None) -> dict:
    """
    Index a video file by extracting keyframes at regular intervals and uploading them for processing.
    
    This function receives a video file, checks if it has a valid video extension,
    runs random access to get a list of images in a temporary folder, uploads them
    to the indexing server, and returns detailed information about the processed frames.
    
    Args:
        video_path: Path to the video file to index
        interval_sec: Interval between frames in seconds (default: 30)
        server_url: URL of the server to upload frames to (default: https://api.zapdoslabs.com)
        progress_callback: Optional callback function to receive progress updates
        api_key: Optional API key for authentication (used as Bearer token)
        
    Returns:
        Dictionary containing:
            - items: List of items with frame details (type, id, timestamp_ms, description)
        
    Raises:
        FileNotFoundError: If the video file does not exist
        ValueError: If the file is not a valid video file
    """
    # Check if file exists
    path = Path(video_path) if isinstance(video_path, str) else video_path
    if not path.exists():
        raise FileNotFoundError(f"Video file '{video_path}' does not exist.")
    
    # Check if file has a valid video extension
    valid_extensions = {
        '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', 
        '.m4v', '.3gp', '.3g2', '.mpg', '.mpeg', '.m2v', '.m4v'
    }
    
    if path.suffix.lower() not in valid_extensions:
        raise ValueError(f"File '{video_path}' is not a valid video file. "
                         f"Supported extensions: {', '.join(valid_extensions)}")
    
    # Create a temporary directory for extracted frames
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "keyframes"
        
        # Extract keyframes and get video metadata
        frame_paths, video_width, video_height, video_duration_ms = extract_keyframes(
            video_path=path,
            output_dir=output_dir,
            interval_sec=interval_sec
        )

        print('Upload and index frames...')
        
        # Upload frames to server
        result = _upload_and_index_frames(
            frame_paths, video_width, video_height, video_duration_ms, server_url, progress_callback, api_key
        )
        
        return result