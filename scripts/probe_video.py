#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from media_common import media_summary, probe_media


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a finished product-demo video.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--min-width", type=int)
    parser.add_argument("--min-height", type=int)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--min-duration", type=float, default=0.1)
    parser.add_argument("--max-duration", type=float)
    parser.add_argument("--video-codec", default="h264")
    parser.add_argument("--audio-codec", default="aac")
    parser.add_argument("--pixel-format", default="yuv420p")
    parser.add_argument("--fps", type=float)
    parser.add_argument("--fps-tolerance", type=float, default=0.05)
    parser.add_argument("--min-fps", type=float)
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--channels", type=int, default=2)
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--full-decode", action="store_true")
    return parser


def validate(summary: dict, args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    video = summary["video"]
    audio = summary["audio"]
    duration = summary["duration"]

    if not video:
        return ["No video stream found"]
    if duration < args.min_duration:
        errors.append(f"Duration {duration:.3f}s is below {args.min_duration:.3f}s")
    if args.max_duration is not None and duration > args.max_duration + 0.05:
        errors.append(f"Duration {duration:.3f}s exceeds {args.max_duration:.3f}s")
    if args.min_width is not None and video["width"] < args.min_width:
        errors.append(f"Width {video['width']} is below {args.min_width}")
    if args.min_height is not None and video["height"] < args.min_height:
        errors.append(f"Height {video['height']} is below {args.min_height}")
    if args.width is not None and video["width"] != args.width:
        errors.append(f"Width {video['width']} does not equal {args.width}")
    if args.height is not None and video["height"] != args.height:
        errors.append(f"Height {video['height']} does not equal {args.height}")
    if args.video_codec and video["codec"] != args.video_codec:
        errors.append(f"Video codec {video['codec']} does not equal {args.video_codec}")
    if args.pixel_format and video["pixelFormat"] != args.pixel_format:
        errors.append(f"Pixel format {video['pixelFormat']} does not equal {args.pixel_format}")
    if args.fps is not None and abs(video["frameRate"] - args.fps) > args.fps_tolerance:
        errors.append(f"Frame rate {video['frameRate']:.3f} does not equal {args.fps:.3f}")
    if args.min_fps is not None and video["frameRate"] < args.min_fps:
        errors.append(f"Frame rate {video['frameRate']:.3f} is below {args.min_fps:.3f}")
    if args.require_audio and not audio:
        errors.append("No audio stream found")
    if audio and args.audio_codec and audio["codec"] != args.audio_codec:
        errors.append(f"Audio codec {audio['codec']} does not equal {args.audio_codec}")
    if audio and args.sample_rate and audio["sampleRate"] != args.sample_rate:
        errors.append(f"Audio sample rate {audio['sampleRate']} does not equal {args.sample_rate}")
    if audio and args.channels and audio["channels"] != args.channels:
        errors.append(f"Audio channels {audio['channels']} does not equal {args.channels}")
    return errors


def full_decode(path: Path) -> str | None:
    import shutil
    import subprocess

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return "Required executable is not on PATH: ffmpeg"
    completed = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(path.resolve()), "-f", "null", "-"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        return completed.stderr.strip() or "Full decode failed"
    if completed.stderr.strip():
        return completed.stderr.strip()
    return None


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = media_summary(args.input, probe_media(args.input))
        errors = validate(summary, args)
        if args.full_decode:
            decode_error = full_decode(args.input)
            if decode_error:
                errors.append(f"Decode check failed: {decode_error}")
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(json.dumps(summary, indent=2))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: media satisfies all requested constraints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
