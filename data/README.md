# data/ Directory

This folder contains data used in the project. To keep the repository lightweight and reproducible, only a small sample of the full dataset is included.

## Included Files

- `sample.json`: A randomly selected subset of video metadata (`videos.json`).
- `README.md`: This file.

## Excluded Files

- `videos.json`: The full dataset, excluded to reduce repository size.
- `secret.json`: Contains your API key and should not be shared.

## Why Use a Sample?

- Keeps the repository small and easy to manage
- Prevents sharing data that may change frequently
- Allows others to reproduce the full dataset independently
- Demonstrates responsible data handling

## Reproducing the Full Dataset

Create a `data/secret.json` with your API key:
```json
{
  "YT_API_KEY": "YOUR_API_KEY_HERE"
}
```

```bash
python scripts/api_scrape_channel.py --channel CHANNEL_ID --output data/videos.json
```
