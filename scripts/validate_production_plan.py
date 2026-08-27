#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


MODES = {"walkthrough", "launch", "pitch"}
SOURCE_TYPES = {"live-capture", "recording", "screenshot", "motion-graphic", "generated", "title-card"}
TRUTH_STATES = {"observed", "provided", "illustrative"}
REQUIRED_PURPOSES = {
    "walkthrough": {"context", "workflow", "outcome"},
    "launch": {"hook", "product", "proof", "cta"},
    "pitch": {"problem", "solution", "product", "proof", "cta"},
}
ASPECT_RATIOS = {"16:9", "16:10", "9:16", "1:1", "4:5"}


def require_object(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return {}
    return value


def words(value: Any) -> int:
    return len(re.findall(r"\b[\w'-]+\b", str(value or "")))


def validate_plan(plan: Any) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = require_object(plan, "production plan", errors)
    project = require_object(root.get("project"), "project", errors)
    mode = project.get("mode")
    if mode not in MODES:
        errors.append(f"project.mode must be one of: {', '.join(sorted(MODES))}")

    max_duration = project.get("maxDuration")
    if not isinstance(max_duration, (int, float)) or max_duration <= 0:
        errors.append("project.maxDuration must be a positive number")
        max_duration = 0
    if project.get("aspectRatio") not in ASPECT_RATIOS:
        errors.append(f"project.aspectRatio must be one of: {', '.join(sorted(ASPECT_RATIOS))}")
    for key in ("title", "audience", "objective"):
        if not isinstance(project.get(key), str) or not project[key].strip():
            errors.append(f"project.{key} must be a non-empty string")

    truth_sources = root.get("truthSources")
    if not isinstance(truth_sources, list) or not truth_sources:
        errors.append("truthSources must be a non-empty array")
        truth_sources = []
    source_ids: set[str] = set()
    for index, source in enumerate(truth_sources):
        source = require_object(source, f"truthSources[{index}]", errors)
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"truthSources[{index}].id must be a non-empty string")
        elif source_id in source_ids:
            errors.append(f"duplicate truth source id: {source_id}")
        else:
            source_ids.add(source_id)
        if not isinstance(source.get("location"), str) or not source["location"].strip():
            errors.append(f"truthSources[{index}].location must be a non-empty string")

    audio = require_object(root.get("audio"), "audio", errors)
    audio_mode = audio.get("mode")
    if audio_mode not in {"silent", "music", "voiceover"}:
        errors.append("audio.mode must be silent, music, or voiceover")

    scenes = root.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes must be a non-empty array")
        scenes = []
    scene_ids: set[str] = set()
    purposes: set[str] = set()
    total_duration = 0.0
    for index, scene_value in enumerate(scenes):
        scene = require_object(scene_value, f"scenes[{index}]", errors)
        scene_id = scene.get("id")
        if not isinstance(scene_id, str) or not scene_id.strip():
            errors.append(f"scenes[{index}].id must be a non-empty string")
        elif scene_id in scene_ids:
            errors.append(f"duplicate scene id: {scene_id}")
        else:
            scene_ids.add(scene_id)
        duration = scene.get("duration")
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append(f"scenes[{index}].duration must be a positive number")
            duration = 0
        total_duration += float(duration)
        purpose = scene.get("purpose")
        if isinstance(purpose, str):
            purposes.add(purpose)
        else:
            errors.append(f"scenes[{index}].purpose must be a string")

        source = require_object(scene.get("source"), f"scenes[{index}].source", errors)
        source_type = source.get("type")
        truth_state = source.get("truthStatus")
        if source_type not in SOURCE_TYPES:
            errors.append(f"scenes[{index}].source.type is unsupported")
        if truth_state not in TRUTH_STATES:
            errors.append(f"scenes[{index}].source.truthStatus is unsupported")
        source_id = source.get("truthSourceId")
        if truth_state in {"observed", "provided"} and source_id not in source_ids:
            errors.append(f"scenes[{index}] must link observed or provided footage to a truth source")
        if source_type in {"generated", "motion-graphic", "title-card"} and truth_state == "observed":
            errors.append(f"scenes[{index}] cannot label constructed visuals as observed")
        if purpose == "proof" and truth_state == "illustrative":
            errors.append(f"scenes[{index}] cannot use an illustrative scene as proof")

        copy = require_object(scene.get("copy", {}), f"scenes[{index}].copy", errors)
        narration = str(copy.get("voiceover") or "")
        on_screen = " ".join(str(copy.get(key) or "") for key in ("title", "body")).strip()
        if audio_mode == "voiceover" and narration:
            rate = words(narration) / max(float(duration), 0.001)
            if rate > 3.1:
                errors.append(f"scenes[{index}] voiceover is too dense at {rate:.1f} words/second")
            elif rate > 2.7:
                warnings.append(f"scenes[{index}] voiceover is fast at {rate:.1f} words/second")
        if audio_mode != "voiceover" and not on_screen and purpose not in {"context", "workflow", "product"}:
            warnings.append(f"scenes[{index}] has no voiceover or explanatory on-screen copy")

    if max_duration and total_duration > float(max_duration) + 0.001:
        errors.append(f"scene duration total {total_duration:.2f}s exceeds the {float(max_duration):.2f}s ceiling")
    if max_duration and total_duration < float(max_duration) * 0.55:
        warnings.append("the plan uses less than 55% of the available duration")
    if mode in REQUIRED_PURPOSES:
        missing = REQUIRED_PURPOSES[mode] - purposes
        if missing:
            errors.append(f"{mode} plan is missing required purposes: {', '.join(sorted(missing))}")
    if mode in {"launch", "pitch"} and scenes:
        first_purpose = scenes[0].get("purpose") if isinstance(scenes[0], dict) else None
        if first_purpose not in {"hook", "problem", "outcome"}:
            warnings.append("the opening scene does not establish a hook, problem, or outcome")

    summary = {
        "mode": mode,
        "scenes": len(scenes),
        "duration": round(total_duration, 3),
        "maxDuration": max_duration,
        "truthSources": len(source_ids),
        "purposes": sorted(purposes),
    }
    return errors, warnings, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a truth-linked product video production plan.")
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        errors, warnings, summary = validate_plan(plan)
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2))
    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print("PASS: production plan is coherent and truth-linked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
