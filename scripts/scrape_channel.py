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

def scrape_channel(channel_url, output_path="data/videos.json"):
    """
    Scrapes metadata for all videos from a given YouTube channel.

    Parameters:
        channel_url (str): URL of the target YouTube channel.
        output_path (str): Path to save the extracted video metadata as JSON.
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": "in_playlist",  # Only get metadata, not video files
        "skip_download": True,
        "forcejson": True,
    }

    with yt.YoutubeDL(ydl_opts) as ydl:
        print(f"Scraping metadata from: {channel_url}")
        result = ydl.extract_info(channel_url, download=False)

        if "entries" not in result:
            print("No video entries found.")
            return

        videos = []
        for video in result["entries"]:
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            print(f"Processing: {video['title']}")

            # Get full metadata for the individual video
            video_info = ydl.extract_info(video_url, download=False)

            # Extract selected fields
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

    # Ensure the data folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

    print(f"\n Saved {len(videos)} videos to {output_path}")


if __name__ == "__main__":
    fliptop_url = "https://www.youtube.com/@fliptopbattles"  
    scrape_channel(fliptop_url)
