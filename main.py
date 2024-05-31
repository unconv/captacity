#!/usr/bin/env python3

from captacity import add_captions
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <video_file> <output_file>")
        sys.exit(1)

    video_file = sys.argv[1]
    output_file = sys.argv[2]

    add_captions(video_file, output_file, print_info=True)
