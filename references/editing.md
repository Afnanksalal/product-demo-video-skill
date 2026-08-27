# FFmpeg finishing and editorial direction

Use this reference when trimming or finishing captured footage.

## Contents

- Edit priorities
- Framing, crop, zoom, and pan
- Captions and safe areas
- Transitions and pacing
- Music and audio
- Export settings
- Reproducibility

## Edit priorities

Make the smallest set of edits that turns the raw interaction into a clear product demonstration:

1. remove loading, failed actions, dead time, and accidental motion;
2. establish consistent framing and hide irrelevant browser chrome;
3. add restrained motion only where it directs attention;
4. add captions only when the screen does not explain itself quickly enough;
5. mix licensed music under the interface or voice track;
6. finish with deliberate opening and ending holds or fades.

Do not cover important controls with decoration. The product is the visual subject.

## Framing, crop, zoom, and pan

- Crop browser or application chrome only when the remaining content still has comfortable margins.
- If a crop leaves half of a navigation bar, either keep the full bar or crop past it cleanly.
- Use a constant crop for structural cleanup. Use animated zooms for emphasis, not to repair inconsistent capture framing.
- Favor 1.08x to 1.25x interface zooms. Deeper zooms require a clear target and a safe exit.
- Ease into and out of motion. Linear movement reads as mechanical and can make scrolling feel jittery.
- Hold the destination long enough to understand the highlighted result.
- Preserve the pointer target and caption safe area while panning.

For a basic static cleanup, use crop, scale, and pad in that order. The bundled finishing script expresses crop as left, top, right, and bottom margins, then scales the visible region to fit or cover the target canvas.

For custom keyframed motion, use FFmpeg filters such as `zoompan`, `crop`, `scale`, and `xfade`, or the user's installed non-linear editor. Keep the motion plan in a checked-in project file or written timing table so it can be reproduced.

## Captions and safe areas

Silent demos need captions that explain the current action or result without narrating every click.

- Title: short action or feature name, usually two to six words.
- Body: one concise sentence describing the input, state change, or proof.
- Use a smaller body size than the title.
- Keep both within a single visual block.
- Place bottom captions at least 6 percent of frame height above the edge.
- Maintain at least 5 percent horizontal safe margin.
- Use high contrast, a subtle background or shadow, and a readable product-adjacent font.
- Avoid em dashes, excessive punctuation, and marketing filler when the product itself is visible.
- Do not repeat visible headings word for word unless the repetition helps orientation.

The finishing script writes Advanced SubStation Alpha captions so title and body sizes can differ. Keep caption timing aligned to the result, not merely the click that initiated it.

## Transitions and pacing

- Use straight cuts inside one workflow.
- Use a 150 to 350 ms dissolve or dip only between distinct sections or takes.
- Do not add a transition to every click.
- Let high-information screens breathe for 1.5 to 4 seconds depending on density.
- Accelerate idle waits before removing feature coverage.
- Trim incomplete first frames and leave a clean final hold before fade-out.
- Keep total runtime at or below the requested ceiling after all fades and crossfades.

## Music and audio

Use music the user supplied or a track with clear commercial-use terms. Save a provenance note containing track title, artist, source page, license, retrieval date, and any modifications.

- Product-launch demos generally work better with rhythmic, forward-moving tracks than ambient relaxation music.
- Loop short tracks with an equal-power crossfade. Never hard-restart a waveform at the loop point.
- When two passes fall only slightly short or long, apply a subtle tempo adjustment rather than adding a distracting partial third pass.
- Start and end the full mix with short fades.
- If there is no voiceover, keep music energetic but below clipping.
- If there is voiceover, reduce music by roughly 12 to 20 dB under speech and verify intelligibility on laptop speakers.
- Normalize deliberately. Do not stack normalization and limiting without listening for pumping.

The finishing script can chain as many copies of a music track as needed, crossfade each boundary, make a bounded tempo adjustment to fit the edit, trim to the video duration, and mix optional source audio. It also accepts a separate voiceover file, normalizes it, and ducks music under speech. Read `audio.md` before using those controls.

## Export settings

Default delivery profile:

- container: MP4;
- video: H.264 High profile, `yuv420p`, constant frame rate;
- audio: AAC, 48 kHz, stereo;
- web playback: `+faststart`;
- quality: CRF 17 to 20 for a high-resolution master;
- frame rate: 30 fps unless the source or destination requires another rate.

Use 2560x1600 or another high-resolution source only when the UI remains sharp and the destination accepts it. A smaller delivery copy can be derived from the master later.

## Reproducibility

Keep these items until the user accepts the result:

- immutable raw recording;
- capture plan;
- finish plan;
- caption text and timings;
- music provenance;
- final FFmpeg command or editor project;
- technical probe output.

Delete extracted frames, failed encodes, browser caches, and obsolete copies only after the accepted master is preserved.
