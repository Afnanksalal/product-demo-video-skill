#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed")
    values: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        if not raw_line or raw_line.startswith(" ") or ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validate_skill(root: Path) -> list[str]:
    errors: list[str] = []
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return ["SKILL.md is missing"]
    try:
        text = skill_path.read_text(encoding="utf-8")
        metadata = parse_frontmatter(text)
    except Exception as error:
        return [str(error)]

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not NAME_PATTERN.fullmatch(name):
        errors.append("name must use lowercase letters, digits, and single hyphens")
    if name != root.name:
        errors.append(f"name {name!r} must match directory name {root.name!r}")
    if len(name) > 64:
        errors.append("name exceeds 64 characters")
    if not description:
        errors.append("description is required")
    if len(description) > 1024:
        errors.append("description exceeds 1024 characters")
    if "TODO" in text or "[TODO" in text:
        errors.append("unfinished TODO marker found in SKILL.md")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md exceeds the recommended 500-line limit")

    for relative in (
        "agents/openai.yaml",
        "scripts/capture_demo.mjs",
        "scripts/finish_video.py",
        "scripts/probe_video.py",
        "references/capture.md",
        "references/editing.md",
        "references/quality.md",
    ):
        if not (root / relative).is_file():
            errors.append(f"referenced file is missing: {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate this Agent Skill package.")
    parser.add_argument("path", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    root = args.path.resolve()
    errors = validate_skill(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {root} is a valid product-demo-video skill package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
