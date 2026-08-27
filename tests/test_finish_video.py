from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from finish_video import ass_escape, ass_time, css_to_ass, music_loop_plan, music_repetitions  # noqa: E402
from media_common import media_summary, parse_fraction  # noqa: E402
from probe_video import validate  # noqa: E402


class FinishVideoTests(unittest.TestCase):
    def test_ass_time_rounds_to_centiseconds(self) -> None:
        self.assertEqual(ass_time(65.129), "0:01:05.13")

    def test_css_rgba_converts_to_ass_alpha_and_bgr(self) -> None:
        self.assertEqual(css_to_ass("#11223380", "#000000"), "&H7F332211&")

    def test_ass_escape_preserves_literal_braces_and_newlines(self) -> None:
        self.assertEqual(ass_escape("A{B}\nC"), r"A\{B\}\NC")

    def test_music_repetitions_accounts_for_crossfades(self) -> None:
        self.assertEqual(music_repetitions(278.0, 139.0, 2.0), 3)
        self.assertEqual(music_repetitions(100.0, 139.0, 2.0), 1)

    def test_music_loop_plan_uses_subtle_tempo_fit_instead_of_partial_loop(self) -> None:
        repetitions, tempo = music_loop_plan(278.0, 139.0, 2.0, 2.5)
        self.assertEqual(repetitions, 2)
        self.assertAlmostEqual(tempo, 276.0 / 278.0)

    def test_fraction_parser_handles_video_rates(self) -> None:
        self.assertAlmostEqual(parse_fraction("30000/1001"), 29.97002997, places=6)

    def test_probe_validation_reports_constraint_failures(self) -> None:
        probe = {
            "format": {"duration": "301", "size": "100", "format_name": "mov,mp4"},
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1280,
                    "height": 720,
                    "pix_fmt": "yuv420p",
                    "avg_frame_rate": "30/1",
                }
            ],
        }
        summary = media_summary("demo.mp4", probe)

        class Args:
            min_duration = 0.1
            max_duration = 300
            min_width = 1920
            min_height = None
            width = None
            height = None
            video_codec = "h264"
            pixel_format = "yuv420p"
            fps = 30
            fps_tolerance = 0.05
            min_fps = None
            require_audio = True
            audio_codec = "aac"
            sample_rate = 48000
            channels = 2

        errors = validate(summary, Args())
        self.assertTrue(any("exceeds" in error for error in errors))
        self.assertTrue(any("Width" in error for error in errors))
        self.assertIn("No audio stream found", errors)


if __name__ == "__main__":
    unittest.main()
