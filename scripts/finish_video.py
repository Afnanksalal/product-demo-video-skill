#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from media_common import duration_seconds, first_stream, probe_media, require_binary


def number(value: Any, default: float, label: str, minimum: float = 0.0) -> float:
    if value is None:
        return default
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise ValueError(f"{label} must be a number greater than or equal to {minimum}")
    return float(value)


def integer(value: Any, default: int, label: str, minimum: int = 1) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or value < minimum:
        raise ValueError(f"{label} must be an integer greater than or equal to {minimum}")
    return value


def resolve_path(plan_directory: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty path string")
    candidate = Path(value)
    return (candidate if candidate.is_absolute() else plan_directory / candidate).resolve()


def css_to_ass(value: str, default: str) -> str:
    raw = (value or default).lstrip("#")
    if len(raw) not in (6, 8) or any(character not in "0123456789abcdefABCDEF" for character in raw):
        raise ValueError(f"Invalid hex color: {value}")
    red, green, blue = raw[0:2], raw[2:4], raw[4:6]
    css_alpha = int(raw[6:8], 16) if len(raw) == 8 else 255
    ass_alpha = 255 - css_alpha
    return f"&H{ass_alpha:02X}{blue.upper()}{green.upper()}{red.upper()}&"


def ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole_seconds, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{fraction:02d}"


def ass_escape(value: str) -> str:
    return (
        str(value)
        .replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\r\n", r"\N")
        .replace("\n", r"\N")
    )


def ffmpeg_filter_path(path: Path) -> str:
    value = path.resolve().as_posix()
    return value.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def write_ass(
    path: Path,
    captions: list[dict[str, Any]],
    style: dict[str, Any],
    width: int,
    height: int,
    duration: float,
) -> None:
    font = str(style.get("font", "Inter")).replace(",", " ")
    title_size = integer(style.get("titleSize"), 50, "captionStyle.titleSize")
    body_size = integer(style.get("bodySize"), 30, "captionStyle.bodySize")
    margin_h = integer(style.get("marginHorizontal"), max(60, width // 18), "captionStyle.marginHorizontal")
    margin_v = integer(style.get("marginVertical"), max(70, height // 14), "captionStyle.marginVertical")
    text_color = css_to_ass(style.get("textColor", "#FFFFFF"), "#FFFFFF")
    accent_color = css_to_ass(style.get("accentColor", "#34D399"), "#34D399")
    background_color = css_to_ass(style.get("backgroundColor", "#111827D9"), "#111827D9")

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "ScaledBorderAndShadow: yes",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{font},{body_size},{text_color},{text_color},{background_color},{background_color},0,0,0,0,100,100,0,0,3,10,0,2,{margin_h},{margin_h},{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for index, caption in enumerate(captions):
        if not isinstance(caption, dict):
            raise ValueError(f"captions[{index}] must be an object")
        start = number(caption.get("start"), 0, f"captions[{index}].start")
        end = number(caption.get("end"), 0, f"captions[{index}].end")
        if end <= start or end > duration + 0.05:
            raise ValueError(f"captions[{index}] has invalid start/end for a {duration:.3f}s video")
        title = ass_escape(caption.get("title", ""))
        body = ass_escape(caption.get("body", ""))
        if not title and not body:
            raise ValueError(f"captions[{index}] must include title or body")
        alignment = 8 if caption.get("position", "bottom") == "top" else 2
        pieces: list[str] = []
        if title:
            pieces.append(f"{{\\an{alignment}\\fs{title_size}\\b1\\c{accent_color}}}{title}")
        if body:
            if pieces:
                pieces.append(r"\N")
            pieces.append(f"{{\\r\\an{alignment}\\fs{body_size}\\c{text_color}}}{body}")
        lines.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{''.join(pieces)}"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_video_chain(
    config: dict[str, Any],
    input_probe: dict[str, Any],
    trim_start: float,
    duration: float,
    ass_path: Path | None,
) -> tuple[str, int, int, int]:
    canvas = config.get("canvas") or {}
    if not isinstance(canvas, dict):
        raise ValueError("canvas must be an object")
    width = integer(canvas.get("width"), 1920, "canvas.width")
    height = integer(canvas.get("height"), 1080, "canvas.height")
    fps = integer(canvas.get("fps"), 30, "canvas.fps")
    if width % 2 or height % 2:
        raise ValueError("canvas width and height must be even")
    fit = canvas.get("fit", "contain")
    if fit not in ("contain", "cover"):
        raise ValueError("canvas.fit must be contain or cover")

    source_video = first_stream(input_probe, "video")
    if not source_video:
        raise ValueError("input has no video stream")
    source_width = int(source_video["width"])
    source_height = int(source_video["height"])
    crop = config.get("crop") or {}
    if not isinstance(crop, dict):
        raise ValueError("crop must be an object")
    left = integer(crop.get("left"), 0, "crop.left", 0)
    top = integer(crop.get("top"), 0, "crop.top", 0)
    right = integer(crop.get("right"), 0, "crop.right", 0)
    bottom = integer(crop.get("bottom"), 0, "crop.bottom", 0)
    if left + right >= source_width or top + bottom >= source_height:
        raise ValueError("crop margins remove the entire input frame")

    chain = [
        f"trim=start={trim_start:.6f}:duration={duration:.6f}",
        "setpts=PTS-STARTPTS",
    ]
    if any((left, top, right, bottom)):
        chain.append(f"crop=iw-{left + right}:ih-{top + bottom}:{left}:{top}")
    if fit == "cover":
        chain.extend(
            [
                f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos",
                f"crop={width}:{height}",
            ]
        )
    else:
        color = str(canvas.get("background", "#0B0D10")).lstrip("#")[:6]
        chain.extend(
            [
                f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos",
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x{color}",
            ]
        )
    chain.append(f"fps={fps}")
    if ass_path:
        chain.append(f"subtitles='{ffmpeg_filter_path(ass_path)}'")
    fade = config.get("fade") or {}
    if not isinstance(fade, dict):
        raise ValueError("fade must be an object")
    fade_in = number(fade.get("in"), 0.4, "fade.in")
    fade_out = number(fade.get("out"), 0.6, "fade.out")
    if fade_in > 0:
        chain.append(f"fade=t=in:st=0:d={min(fade_in, duration):.6f}")
    if fade_out > 0:
        chain.append(f"fade=t=out:st={max(0, duration - fade_out):.6f}:d={min(fade_out, duration):.6f}")
    chain.append("format=yuv420p")
    return f"[0:v]{','.join(chain)}[vout]", width, height, fps


def build_audio_filters(
    config: dict[str, Any],
    input_probe: dict[str, Any],
    trim_start: float,
    duration: float,
    music_probe: dict[str, Any] | None,
    music_input_count: int,
    music_tempo: float,
) -> list[str]:
    music = config.get("music") or {}
    fade = config.get("fade") or {}
    fade_in = number(fade.get("in"), 0.4, "fade.in")
    fade_out = number(fade.get("out"), 0.6, "fade.out")
    filters: list[str] = []
    music_label: str | None = None

    if music_probe and music_input_count:
        crossfade = number(music.get("crossfade"), 2.0, "music.crossfade")
        for index in range(music_input_count):
            input_index = index + 1
            filters.append(
                f"[{input_index}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[m{index}]"
            )
        current = "m0"
        for index in range(1, music_input_count):
            next_label = f"mx{index}"
            filters.append(
                f"[{current}][m{index}]acrossfade=d={crossfade:.6f}:c1=qsin:c2=qsin[{next_label}]"
            )
            current = next_label
        volume = number(music.get("volume"), 0.22, "music.volume")
        tempo_filter = "" if abs(music_tempo - 1.0) < 0.000001 else f"atempo={music_tempo:.9f},"
        filters.append(
            f"[{current}]{tempo_filter}atrim=duration={duration:.6f},asetpts=PTS-STARTPTS,volume={volume:.6f}[musicbed]"
        )
        music_label = "musicbed"

    keep_source = bool(music.get("keepSourceAudio", config.get("keepSourceAudio", False)))
    source_audio = first_stream(input_probe, "audio")
    source_label: str | None = None
    if keep_source and source_audio:
        source_volume = number(music.get("sourceVolume"), 1.0, "music.sourceVolume")
        filters.append(
            f"[0:a]atrim=start={trim_start:.6f}:duration={duration:.6f},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume={source_volume:.6f}[sourceaudio]"
        )
        source_label = "sourceaudio"

    if source_label and music_label:
        filters.append(
            f"[{source_label}][{music_label}]amix=inputs=2:duration=first:dropout_transition=0[mixed]"
        )
        current_audio = "mixed"
    elif source_label:
        current_audio = source_label
    elif music_label:
        current_audio = music_label
    else:
        filters.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={duration:.6f}[silence]")
        current_audio = "silence"

    finish = ["alimiter=limit=0.95"]
    if fade_in > 0:
        finish.append(f"afade=t=in:st=0:d={min(fade_in, duration):.6f}")
    if fade_out > 0:
        finish.append(
            f"afade=t=out:st={max(0, duration - fade_out):.6f}:d={min(fade_out, duration):.6f}"
        )
    filters.append(f"[{current_audio}]{','.join(finish)}[aout]")
    return filters


def music_repetitions(duration: float, music_duration: float, crossfade: float) -> int:
    if music_duration <= 0:
        raise ValueError("music duration must be positive")
    if crossfade < 0 or crossfade >= music_duration:
        raise ValueError("music.crossfade must be shorter than the music track")
    if duration <= music_duration:
        return 1
    return 1 + math.ceil((duration - music_duration) / (music_duration - crossfade))


def music_loop_plan(
    duration: float,
    music_duration: float,
    crossfade: float,
    max_tempo_adjustment_percent: float,
) -> tuple[int, float]:
    fallback = music_repetitions(duration, music_duration, crossfade)
    limit = max_tempo_adjustment_percent / 100.0
    candidates: list[tuple[float, int, float]] = []
    for repetitions in range(1, fallback + 2):
        natural_duration = repetitions * music_duration - (repetitions - 1) * crossfade
        tempo = natural_duration / duration
        adjustment = abs(tempo - 1.0)
        if 0.5 <= tempo <= 2.0 and adjustment <= limit:
            candidates.append((adjustment, repetitions, tempo))
    if not candidates:
        return fallback, 1.0
    _, repetitions, tempo = min(candidates)
    return repetitions, tempo


def finish(plan_path: Path) -> Path:
    absolute_plan = plan_path.resolve()
    plan_directory = absolute_plan.parent
    config = json.loads(absolute_plan.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("finish plan must contain a JSON object")

    input_path = resolve_path(plan_directory, config.get("input"), "input")
    output_path = resolve_path(plan_directory, config.get("output"), "output")
    if output_path.exists() and not config.get("overwrite", False):
        raise FileExistsError(f"output already exists: {output_path}; set overwrite to true to replace it")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = output_path.with_name(f".{output_path.stem}.partial{output_path.suffix}")
    ass_path = output_path.with_name(f".{output_path.stem}.captions.ass")
    partial_path.unlink(missing_ok=True)
    ass_path.unlink(missing_ok=True)

    ffmpeg = require_binary("ffmpeg")
    input_probe = probe_media(input_path)
    input_duration = duration_seconds(input_probe)
    trim_start = number(config.get("trimStart"), 0, "trimStart")
    trim_end_value = config.get("trimEnd")
    trim_end = input_duration if trim_end_value is None else number(trim_end_value, input_duration, "trimEnd")
    if trim_start >= input_duration or trim_end <= trim_start or trim_end > input_duration + 0.05:
        raise ValueError(f"trim range {trim_start:.3f}..{trim_end:.3f} is invalid for {input_duration:.3f}s input")
    duration = trim_end - trim_start
    max_duration = config.get("maxDuration")
    if max_duration is not None:
        duration = min(duration, number(max_duration, duration, "maxDuration", 0.1))

    captions = config.get("captions") or []
    if not isinstance(captions, list):
        raise ValueError("captions must be an array")
    canvas = config.get("canvas") or {}
    width = integer(canvas.get("width"), 1920, "canvas.width")
    height = integer(canvas.get("height"), 1080, "canvas.height")
    if captions:
        write_ass(ass_path, captions, config.get("captionStyle") or {}, width, height, duration)

    video_filter, width, height, fps = build_video_chain(
        config, input_probe, trim_start, duration, ass_path if captions else None
    )

    command = [ffmpeg, "-hide_banner", "-y", "-i", str(input_path)]
    music = config.get("music") or {}
    if not isinstance(music, dict):
        raise ValueError("music must be an object")
    music_path: Path | None = None
    music_probe: dict[str, Any] | None = None
    repetitions = 0
    music_tempo = 1.0
    if music.get("path"):
        music_path = resolve_path(plan_directory, music["path"], "music.path")
        music_probe = probe_media(music_path)
        if not first_stream(music_probe, "audio"):
            raise ValueError("music file has no audio stream")
        crossfade = number(music.get("crossfade"), 2.0, "music.crossfade")
        max_adjustment = number(
            music.get("maxTempoAdjustmentPercent"),
            2.5,
            "music.maxTempoAdjustmentPercent",
        )
        repetitions, music_tempo = music_loop_plan(
            duration,
            duration_seconds(music_probe),
            crossfade,
            max_adjustment,
        )
        for _ in range(repetitions):
            command.extend(["-i", str(music_path)])

    filters = [video_filter]
    filters.extend(
        build_audio_filters(
            config,
            input_probe,
            trim_start,
            duration,
            music_probe,
            repetitions,
            music_tempo,
        )
    )
    encoding = config.get("encoding") or {}
    if not isinstance(encoding, dict):
        raise ValueError("encoding must be an object")
    crf = integer(encoding.get("crf"), 18, "encoding.crf", 0)
    preset = str(encoding.get("preset", "slow"))
    audio_bitrate = str(encoding.get("audioBitrate", "192k"))

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-profile:v",
            "high",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(fps),
            "-c:a",
            "aac",
            "-b:a",
            audio_bitrate,
            "-ar",
            "48000",
            "-ac",
            "2",
            "-t",
            f"{duration:.6f}",
            "-movflags",
            "+faststart",
            str(partial_path),
        ]
    )

    print("Running:")
    print(shlex.join(command))
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        partial_path.unlink(missing_ok=True)
        raise RuntimeError(f"FFmpeg failed with exit code {completed.returncode}")

    validator = Path(__file__).with_name("probe_video.py")
    validation_command = [
        sys.executable,
        str(validator),
        str(partial_path),
        "--width",
        str(width),
        "--height",
        str(height),
        "--fps",
        str(fps),
        "--require-audio",
        "--max-duration",
        f"{duration + 0.02:.6f}",
    ]
    if config.get("fullDecode", False):
        validation_command.append("--full-decode")
    validation = subprocess.run(validation_command, check=False)
    if validation.returncode != 0:
        raise RuntimeError("Finished video did not pass technical validation")

    os.replace(partial_path, output_path)
    ass_path.unlink(missing_ok=True)
    print(f"Finished video: {output_path}")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Finish a real-product demo with FFmpeg.")
    parser.add_argument("plan", type=Path, help="Path to a finish-plan JSON file")
    args = parser.parse_args()
    try:
        finish(args.plan)
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
