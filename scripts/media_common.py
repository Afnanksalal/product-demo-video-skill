from __future__ import annotations

import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any


def require_binary(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"Required executable is not on PATH: {name}")
    return resolved


def run_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"Command failed ({completed.returncode}): {detail}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Command returned invalid JSON") from error


def probe_media(path: str | Path) -> dict[str, Any]:
    media_path = Path(path).resolve()
    if not media_path.is_file():
        raise FileNotFoundError(f"Media file does not exist: {media_path}")
    ffprobe = require_binary("ffprobe")
    return run_json(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size,format_name,start_time:stream=index,codec_name,codec_type,width,height,pix_fmt,r_frame_rate,avg_frame_rate,sample_rate,channels,channel_layout",
            "-of",
            "json",
            str(media_path),
        ]
    )


def first_stream(probe: dict[str, Any], codec_type: str) -> dict[str, Any] | None:
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == codec_type:
            return stream
    return None


def parse_fraction(value: str | int | float | None) -> float:
    if value in (None, "", "0/0"):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(Fraction(value))


def duration_seconds(probe: dict[str, Any]) -> float:
    try:
        return float(probe["format"]["duration"])
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError("Media duration is unavailable") from error


def media_summary(path: str | Path, probe: dict[str, Any]) -> dict[str, Any]:
    video = first_stream(probe, "video")
    audio = first_stream(probe, "audio")
    return {
        "path": str(Path(path).resolve()),
        "duration": duration_seconds(probe),
        "size": int(probe.get("format", {}).get("size", 0)),
        "container": probe.get("format", {}).get("format_name"),
        "video": None
        if not video
        else {
            "codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "pixelFormat": video.get("pix_fmt"),
            "frameRate": parse_fraction(video.get("avg_frame_rate") or video.get("r_frame_rate")),
        },
        "audio": None
        if not audio
        else {
            "codec": audio.get("codec_name"),
            "sampleRate": int(audio.get("sample_rate", 0)),
            "channels": audio.get("channels"),
            "channelLayout": audio.get("channel_layout"),
        },
    }
