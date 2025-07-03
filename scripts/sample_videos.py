import json
import random
import argparse
import os

def sample_videos(input_path, output_path, n, seed=42):
    """
    Randomly samples `n` videos from `input_path` and writes them to `output_path`.

    Parameters:
        input_path (str): Path to the full JSON file (e.g., videos.json).
        output_path (str): Path to write the sampled subset (e.g., sample.json).
        n (int): Number of videos to sample.
        seed (int): Seed for random sampling to ensure reproducibility.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        all_videos = json.load(f)

    if n > len(all_videos):
        raise ValueError(f"Requested {n} samples, but only {len(all_videos)} videos available.")

    random.seed(seed)
    sampled = random.sample(all_videos, n)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sampled, f, indent=2, ensure_ascii=False)

    print(f"Sampled {n} videos written to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Randomly sample videos from a full dataset.")
    parser.add_argument("--input", required=True, help="Path to full JSON file (e.g., videos.json)")
    parser.add_argument("--output", required=True, help="Path to save sampled JSON file (e.g., sample.json)")
    parser.add_argument("--n", type=int, required=True, help="Number of videos to sample")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    args = parser.parse_args()

    try:
        sample_videos(args.input, args.output, args.n, args.seed)
    except Exception as e:
        print(f"Error: {e}")
