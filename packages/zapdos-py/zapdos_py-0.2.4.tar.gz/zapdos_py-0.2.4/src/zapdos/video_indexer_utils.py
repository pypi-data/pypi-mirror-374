import os
import aiohttp
import asyncio
import jsonlines
import json
from typing import List, Optional, Callable
from .definitions import IndexEvents
import re

async def _upload_batch(session, batch_files, batch_timestamps, base_data, server_url, progress_callback, semaphore, items, api_key=None):
    """
    Upload a single batch asynchronously. Semaphore controls when batch can start.
    """
    async with semaphore:
        data = base_data.copy()
        files = {}

        # Prepare files for aiohttp multipart upload
        for idx, (filename, file_path) in enumerate(batch_files):
            data[f"timestamp_{idx}"] = str(batch_timestamps[idx])
            files[f"frame_{idx}"] = open(file_path, "rb")

        try:
            # aiohttp multipart POST
            form = aiohttp.FormData()
            for k, f in files.items():
                form.add_field(k, f, filename=os.path.basename(f.name), content_type="image/jpeg")
            for k, v in data.items():
                form.add_field(k, v)

            # Add authorization header if API key is provided
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            async with session.post(f"{server_url}/index", data=form, headers=headers, timeout=aiohttp.ClientTimeout(total=180)) as resp:
                if resp.status in [200, 201, 207]:
                    # Process streaming response line by line
                    async for line in resp.content:
                        try:
                            event_data = json.loads(line.decode())
                        except Exception:
                            continue

                        event_type = event_data.get("event", "unknown")

                        # Call progress callback
                        if progress_callback:
                            progress_callback(event_data)

                        # DONE_INDEXING: collect items and summary
                        if event_type == IndexEvents.DONE_INDEXING:
                            batch_items = event_data.get("items", [])
                            items.extend(batch_items)

                        # COMPLETED_IMAGE_DESCRIPTION_JOB: allow next batch to start
                        if event_type == IndexEvents.COMPLETED_IMAGE_DESCRIPTION_JOB:
                            semaphore.release()
                else:
                    print(f"Failed to upload batch: {resp.status} - {await resp.text()}")
        except aiohttp.ClientConnectionError as e:
            print(f"Connection error during upload: {e}")
        except asyncio.TimeoutError as e:
            print(f"Timeout during upload: {e}")
        except Exception as e:
            import traceback
            print(f"Error during upload: {e}")
            traceback.print_exc()
        finally:
            # Close all file handles
            for f in files.values():
                try:
                    f.close()
                except:
                    pass


async def _upload_and_index_frames_async(frame_paths: List[str], video_width: int, video_height: int, video_duration_ms: float,
                                         server_url: str,
                                         progress_callback: Optional[Callable[[dict], None]] = None,
                                         api_key: Optional[str] = None):
    items = []

    # Prepare files and timestamps
    files_to_upload = []
    timestamps = []

    for frame_path in frame_paths:
        filename = os.path.basename(frame_path)
        match = re.search(r'(\d+)ms', filename)
        timestamp_ms = int(match.group(1)) if match else 0
        files_to_upload.append((filename, frame_path))
        timestamps.append(timestamp_ms)

    # Sort by timestamp
    sorted_files_data = sorted(zip(files_to_upload, timestamps), key=lambda x: x[1])
    files_to_upload, timestamps = zip(*sorted_files_data)

    # Batch files - create balanced batches
    total_files = len(files_to_upload)
    batch_size = 50
    num_batches = (total_files + batch_size - 1) // batch_size  # Ceiling division
    
    # If we have more than one batch, balance them
    if num_batches > 1 and total_files % num_batches != 0:
        # Calculate a more balanced batch size
        balanced_batch_size = (total_files + num_batches - 1) // num_batches  # Ceiling division
        batches = [(files_to_upload[i:i + balanced_batch_size], timestamps[i:i + balanced_batch_size])
                   for i in range(0, len(files_to_upload), balanced_batch_size)]
    else:
        # Use fixed batch size if evenly divisible or only one batch
        batches = [(files_to_upload[i:i + batch_size], timestamps[i:i + batch_size])
                   for i in range(0, len(files_to_upload), batch_size)]

    print('Total num batches:', len(batches), 'Batches:', [len(b[0]) for b in batches])

    base_data = {
        "video_width": str(video_width),
        "video_height": str(video_height),
        "video_duration_ms": str(video_duration_ms)
    }

    # Semaphore: allow only first batch to start
    image_description_semaphore = asyncio.Semaphore(1)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for batch_files, batch_timestamps in batches:
            task = asyncio.create_task(_upload_batch(session, batch_files, batch_timestamps, base_data,
                                                     server_url, progress_callback, image_description_semaphore, items, api_key))
            tasks.append(task)

        await asyncio.gather(*tasks)

    return {"items": items}


def _upload_and_index_frames(frame_paths: List[str],
                             video_width: int,
                             video_height: int,
                             video_duration_ms: float,
                             server_url: str,
                             progress_callback: Optional[Callable[[dict], None]] = None,
                             api_key: Optional[str] = None) -> dict:
    """
    Synchronous wrapper for async upload/index.
    """
    return asyncio.run(_upload_and_index_frames_async(
        frame_paths,
        video_width,
        video_height,
        video_duration_ms,
        server_url,
        progress_callback,
        api_key
    ))
