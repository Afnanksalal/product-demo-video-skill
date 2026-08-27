#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

from media_common import duration_seconds, probe_media, require_binary


def layout(count: int) -> tuple[int, int]:
    columns = max(1, math.ceil(math.sqrt(count * 16 / 9)))
    rows = math.ceil(count / columns)
    return columns, rows


def timestamps(duration: float, count: int) -> list[float]:
    if count < 1:
        raise ValueError("count must be positive")
    if duration <= 0:
        raise ValueError("duration must be positive")
    return [round(duration * (index + 0.5) / count, 3) for index in range(count)]


def build_filter(duration: float, count: int, cell_width: int, cell_height: int) -> str:
    columns, rows = layout(count)
    interval = duration / count
    return (
        f"fps=1/{interval:.9f},"
        f"scale={cell_width}:{cell_height}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={cell_width}:{cell_height}:(ow-iw)/2:(oh-ih)/2:color=0x111827,"
        f"tile={columns}x{rows}:nb_frames={count}:padding=8:margin=8:color=0x0B0D10"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a representative-frame contact sheet for video review.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--cell-width", type=int, default=480)
    parser.add_argument("--cell-height", type=int, default=300)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        if args.count < 1 or args.cell_width < 2 or args.cell_height < 2:
            raise ValueError("count and cell dimensions must be positive")
        input_path = args.input.resolve()
        output_path = args.output.resolve()
        if output_path.exists() and not args.overwrite:
            raise FileExistsError(f"output already exists: {output_path}; pass --overwrite to replace it")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        duration = duration_seconds(probe_media(input_path))
        ffmpeg = require_binary("ffmpeg")
        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            build_filter(duration, args.count, args.cell_width, args.cell_height),
            "-frames:v",
            "1",
            str(output_path),
        ]
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            output_path.unlink(missing_ok=True)
            raise RuntimeError(f"FFmpeg failed with exit code {completed.returncode}")
        manifest = output_path.with_suffix(output_path.suffix + ".json")
        manifest.write_text(
            json.dumps(
                {
                    "input": str(input_path),
                    "contactSheet": str(output_path),
                    "duration": round(duration, 3),
                    "sampleTimestamps": timestamps(duration, args.count),
                    "layout": dict(zip(("columns", "rows"), layout(args.count))),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Contact sheet: {output_path}")
        print(f"Manifest: {manifest}")
        return 0
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
