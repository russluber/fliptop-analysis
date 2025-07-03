"""
scrape_channel.py

Extracts metadata from a specified YouTube channel using yt-dlp.
Future versions will store titles, descriptions, view counts, and more
for downstream analysis.

Author: Russel Luber
"""

import yt_dlp as yt
import json
import os
import time
import random

def scrape_channel(channel_url, output_path="data/videos.json", batch_size=100, delay_range=(5, 10), save_every=20):
    """
    Scrapes metadata for all videos from a given YouTube channel in batches.

    Parameters:
        channel_url (str): URL of the target YouTube channel.
        output_path (str): Path to save the extracted video metadata as JSON.
        batch_size (int): Number of videos to process in one run.
        delay_range (tuple): Min and max delay between requests in seconds.
        save_every (int): Save intermediate results every `save_every` videos.
    """
    # Load existing data to resume
    seen_ids = set()
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                seen_ids = {video["id"] for video in existing_data}
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    videos = existing_data
    skipped = 0
    processed = 0

    ydl_opts = {
        "quiet": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "forcejson": True,
    }

    with yt.YoutubeDL(ydl_opts) as ydl:
        print(f"Scraping metadata from: {channel_url}")
        result = ydl.extract_info(channel_url, download=False)

        if "entries" not in result:
            print("No video entries found.")
            return

        for idx, video in enumerate(result["entries"]):
            if processed >= batch_size:
                print(f"\nReached batch limit of {batch_size}. Exiting early.")
                break

            video_id = video.get("id")
            if video_id in seen_ids:
                skipped += 1
                continue

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"Processing [{processed + 1}]: {video.get('title', '[No Title]')}")

            try:
                video_info = ydl.extract_info(video_url, download=False)
                data = {
                    "title": video_info.get("title"),
                    "description": video_info.get("description"),
                    "upload_date": video_info.get("upload_date"),
                    "view_count": video_info.get("view_count"),
                    "duration": video_info.get("duration"),
                    "id": video_info.get("id"),
                    "url": video_info.get("webpage_url"),
                    "tags": video_info.get("tags", []),
                }
                videos.append(data)
                seen_ids.add(video_info.get("id"))
                processed += 1
            except Exception as e:
                print(f"  → Skipping video {video_url} due to error: {e}")

            # Save partial progress every N new videos
            if processed > 0 and processed % save_every == 0:
                print(f"  ⏳ Saving partial results after {processed} videos...")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(videos, f, indent=2, ensure_ascii=False)

            time.sleep(random.uniform(*delay_range))

    # Final save if any new videos were added
    if processed > 0:
        print("\nFinalizing: writing all collected videos to disk...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {processed} new videos ({skipped} skipped) to {output_path}")
    else:
        print("\nNo new videos were scraped. Nothing was saved.")

if __name__ == "__main__":
    fliptop_url = "https://www.youtube.com/@fliptopbattles/videos"
    scrape_channel(fliptop_url)



