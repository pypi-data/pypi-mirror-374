"""CLI module for zapdos video indexing."""

import argparse
import sys
from pathlib import Path
from typing import Union
from .video_indexer import index
from .definitions import IndexEvents
import json
import os

def _progress_callback(event_data):
    """Callback function to handle progress updates."""
    event_type = event_data.get("event", "unknown")
    
    if event_type == IndexEvents.INSERTED_VIDEO_FILE_RECORD:
        video_file_id = event_data.get("video_file_id")
        print(f"✓ Created video file record with ID: {video_file_id}")
    elif event_type == IndexEvents.UPLOADED_FRAME:
        # Only track uploads without printing each one to avoid clutter
        pass
    elif event_type == IndexEvents.INSERTED_FRAMES_RECORDS:
        count = event_data.get("count", 0)
        print(f"💾 Inserted {count} frame records into database")
    elif event_type == IndexEvents.CREATED_IMAGE_DESCRIPTION_JOB:
        job_id = event_data.get("job_id")
        print(f"⚙️  Created image description job with ID: {job_id}")
    elif event_type == IndexEvents.COMPLETED_IMAGE_DESCRIPTION_JOB:
        job_id = event_data.get("job_id")
        print(f"✅ Completed image description job with ID: {job_id}")
    elif event_type == IndexEvents.CREATED_OBJECT_DETECTION_JOB:
        job_id = event_data.get("job_id")
        print(f"🔍 Created object detection job with ID: {job_id}")
    elif event_type == IndexEvents.COMPLETED_OBJECT_DETECTION_JOB:
        job_id = event_data.get("job_id")
        print(f"✅ Completed object detection job with ID: {job_id}")
    elif event_type == IndexEvents.CREATED_SUMMARY_JOB:
        job_id = event_data.get("job_id")
        print(f"📝 Created summary job with ID: {job_id}")
    elif event_type == IndexEvents.COMPLETED_SUMMARY_JOB:
        job_id = event_data.get("job_id")
        print(f"✅ Completed summary job with ID: {job_id}")
    elif event_type == IndexEvents.DONE_INDEXING:
        print(f"🎉 Batch completed")
    elif event_type == IndexEvents.ERROR_INDEXING:
        error_msg = event_data.get("message", "Unknown error")
        print(f"❌ Error: {error_msg}")
    else:
        print(f"ℹ️  Unknown event: {event_data}")

def index_video_file(file_path: Union[str, Path], interval: int = 30, api_key: str = None) -> bool:
    """Index the specified video file by extracting and uploading keyframes.
    
    Args:
        file_path: Path to the video file to index
        interval: Interval between frames in seconds (default: 30)
        api_key: Optional API key for authentication
        
    Returns:
        bool: True if indexing was successful, False otherwise
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    if not path.exists():
        raise FileNotFoundError(f"Video file '{file_path}' does not exist.")
    
    # If no API key provided, try to get it from environment variable
    if not api_key:
        api_key = os.getenv("ZAPDOS_API_KEY")
    
    try:
        print(f"Indexing video file: {path.absolute()}")
        result = index(path, interval_sec=interval, progress_callback=_progress_callback, api_key=api_key)
        print(f"Successfully extracted and indexing {len(result['items'])} frames")
        return True
    except Exception as e:
        print(f"Error indexing video file: {e}")
        return False

def main() -> None:
    """Main entry point for the zapdos CLI."""
    parser = argparse.ArgumentParser(
        description="Zapdos - A CLI tool for indexing video files"
    )
    parser.add_argument(
        "file_path", 
        help="Path to the video file to index"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=30,
        help="Interval between frames in seconds (default: 30)"
    )
    parser.add_argument(
        "--api-key", 
        type=str, 
        help="API key for authentication (can also be set via ZAPDOS_API_KEY environment variable)"
    )
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Handle video indexing
    try:
        success = index_video_file(args.file_path, args.interval, args.api_key)
        if not success:
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()