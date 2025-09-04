"""Client module for zapdos API."""

from typing import Optional, Callable, Union
from pathlib import Path
from .video_indexer import index


class Client:
    """Zapdos API Client.
    
    This client is used to interact with the Zapdos API services.
    """
    
    def __init__(self, api_key: str, server_url: str = "https://api.zapdoslabs.com"):
        """Initialize the Zapdos client.
        
        Args:
            api_key: Your Zapdos API key for authentication
            server_url: The base URL for the Zapdos API (default: https://api.zapdoslabs.com)
        """
        self.api_key = api_key
        self.server_url = server_url
    
    def index(self, video_path: Union[str, Path], interval_sec: int = 30, 
              progress_callback: Optional[Callable[[dict], None]] = None) -> dict:
        """Index a video file by extracting keyframes and uploading them for processing.
        
        Args:
            video_path: Path to the video file to index
            interval_sec: Interval between frames in seconds (default: 30)
            progress_callback: Optional callback function to receive progress updates
            
        Returns:
            Dictionary containing the indexing results
        """
        return index(
            video_path=video_path,
            interval_sec=interval_sec,
            server_url=self.server_url,
            progress_callback=progress_callback,
            api_key=self.api_key
        )