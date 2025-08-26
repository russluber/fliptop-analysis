import os
import json
import time
import requests
import argparse

# Load API key from secret file
with open("data/secret.json", "r", encoding="utf-8") as f:
    secret = json.load(f)

API_KEY = secret["YT_API_KEY"]

def get_uploads_playlist_id(channel_id):
    """
    Retrieves the ID of the 'uploads' playlist associated with a YouTube channel.
    """
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch uploads playlist: {e}")
    except (KeyError, IndexError):
        raise ValueError("Could not retrieve uploads playlist ID.")

def get_all_video_ids(playlist_id):
    """
    Retrieves all video IDs from a YouTube 'uploads' playlist.
    """
    video_ids = []
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": API_KEY
    }

    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch video IDs: {e}")

        for item in data.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        if "nextPageToken" in data:
            params["pageToken"] = data["nextPageToken"]
            time.sleep(0.2)  # gentle pacing
        else:
            break

    return video_ids

def get_video_metadata(video_ids, existing_ids=None):
    """
    Fetches detailed metadata for a list of video IDs using the YouTube Data API.
    """
    if existing_ids is None:
        existing_ids = set()

    video_data = []
    url = "https://www.googleapis.com/youtube/v3/videos"

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        batch = [vid for vid in batch if vid not in existing_ids]

        if not batch:
            continue  # All already scraped

        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(batch),
            "key": API_KEY
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch video metadata: {e}")

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            content_details = item.get("contentDetails", {})

            metadata = {
                "id": item.get("id"),
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "upload_date": snippet.get("publishedAt", ""),
                "view_count": statistics.get("viewCount"),
                "duration": content_details.get("duration", ""),
                "url": f"https://www.youtube.com/watch?v={item.get('id')}",
                "likeCount": statistics.get("likeCount"),
                "commentCount": statistics.get("commentCount"),
                "tags": snippet.get("tags", [])
            }
            video_data.append(metadata)

        time.sleep(0.2)

    return video_data

def scrape_channel_by_id(channel_id, output_path="data/videos.json"):
    """
    Scrapes metadata for all videos uploaded to a given YouTube channel.
    """
    uploads_id = get_uploads_playlist_id(channel_id)
    video_ids = get_all_video_ids(uploads_id)

    # Load existing metadata
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                existing_ids = {video["id"] for video in existing_data}
            except json.JSONDecodeError:
                existing_data = []
                existing_ids = set()
    else:
        existing_data = []
        existing_ids = set()

    print(f"Found {len(video_ids)} total videos. Checking for new ones...")

    # Get metadata for new videos only
    new_data = get_video_metadata(video_ids, existing_ids)

    if new_data:
        all_data = existing_data + new_data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print(f"Added {len(new_data)} new videos. Total now: {len(all_data)}")
    else:
        print("No new videos found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape metadata from a YouTube channel.")
    parser.add_argument(
        "--channel",
        required=True,
        help="The YouTube channel ID (e.g., 'UCBdHwFIE4AJWSa3Wxdu7bAQ')"
    )
    parser.add_argument(
        "--output",
        default="data/videos.json",
        help="Path to save the output JSON file (default: data/videos.json)"
    )
    args = parser.parse_args()

    try:
        scrape_channel_by_id(args.channel, args.output)
    except Exception as e:
        print(f"Error: {e}")

# Run in VS Code integrated terminal like so:
# python .\scripts\api_scrape_channel.py --channel UCBdHwFIE4AJWSa3Wxdu7bAQ --output .\data\videos.json
