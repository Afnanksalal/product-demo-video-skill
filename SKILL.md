---
name: product-demo-video-skill
description: Record and finish polished product demo videos from a real application or website. Use for browser walkthroughs, launch demos, feature tours, raw UI recordings, captions, zooms, music, transitions, and delivery-ready MP4 exports. Prefer real product interaction over recreated or generated interfaces.
license: MIT
metadata:
  author: afnanksalal
  version: "1.0.1"
---

# Product Demo Video Skill

Create a concise, credible demo from the actual product. Record real interactions, finish them with deterministic media tooling, and verify the exported file before delivery.

Do not rebuild the interface in HTML, generate a simulated dashboard, or substitute screenshots for a functioning product unless the user explicitly requests that style. A demo must not imply that a feature or result exists when it was not observed.

## Choose the mode

- **Capture and finish**: Inspect the product, record the flow, edit, and export. Use the full workflow.
- **Capture only**: Record clean source footage and preserve it without overlays or music.
- **Finish existing footage**: Skip product inspection only when the supplied recording and edit brief are sufficient.
- **Repair an export**: Probe the file first, change only the defective parts, and preserve the accepted edit decisions.

Read only the references needed for the selected mode:

- For browser inspection, interaction design, authentication, and recording, read [references/capture.md](references/capture.md).
- For trimming, crop and zoom choices, captions, transitions, music, and FFmpeg finishing, read [references/editing.md](references/editing.md).
- For technical and visual acceptance checks, read [references/quality.md](references/quality.md).

## Non-negotiable rules

1. Inspect before scripting. Learn the current routes, navigation, visible states, and real feature names from the running product or source. Never invent a tab, endpoint, metric, result, or interaction.
2. Show the product in a coherent order. Establish context before performing a transaction or destructive action. For an application demo, a useful default is landing page, overview, primary workflow, resulting output, supporting features, settings, and final overview.
3. Use real interactions. Fill fields, choose options, submit forms, wait for results, open details, and verify the visible outcome. Page hopping alone is not a feature demo.
4. Treat side effects as real. Do not create accounts, purchases, messages, uploads, or production data unless the user authorized those actions. Use test or sandbox systems when available.
5. Keep secrets outside committed plans. Resolve credentials from environment variables, a permitted password manager, or an existing authenticated browser profile. Redact them from logs and intermediate files unless the user explicitly asks for visible raw footage.
6. Preserve the raw master until the final export passes QA. Write intermediates to a dedicated artifact directory, never over the only source.
7. Keep the runtime within the requested ceiling. Tighten pauses and remove dead time before dropping requested feature coverage.
8. Use properly licensed audio and retain source, author, license, and retrieval information beside the project.
9. Do not claim completion from an FFmpeg exit code alone. Probe the output and inspect representative frames, including the opening, every transition, dense UI states, captions, and the ending.

## Workflow

Copy and maintain this checklist during substantial work:

```text
Demo progress
- [ ] Define delivery constraints
- [ ] Inspect the real product
- [ ] Build a timed shot plan
- [ ] Rehearse risky interactions
- [ ] Record a clean raw master
- [ ] Finish picture, captions, and audio
- [ ] Run technical validation
- [ ] Inspect representative frames and playback
- [ ] Preserve source, project metadata, and final export
```

### 1. Define the contract

Determine the destination, aspect ratio, resolution, frame rate, maximum duration, voiceover status, caption style, cursor preference, audio source, and whether real data changes are allowed. Infer ordinary defaults when they do not materially change the outcome:

- Product demos: 16:10 or 16:9 landscape, 30 fps, H.264 video, AAC stereo audio.
- High-resolution master: at least 1920 pixels wide; use the user's requested resolution when specified.
- Browser capture: no visible automation chrome, stable viewport, notifications disabled, and cursor decoration off unless requested.
- Silent demo: concise title plus smaller explanatory line for each important action or result.

### 2. Inspect and map the product

Open the application and enumerate the current navigation, primary workflow, settings, empty states, success states, and responsive behavior. Check source routes when available. Build a feature coverage table with the exact screen, action, expected visible result, and estimated seconds.

Remove duplicate screens and explanatory marketing copy that does not demonstrate behavior. Do not begin the recording at a mid-flow screen unless the brief explicitly requires it.

### 3. Rehearse, then capture

Read [references/capture.md](references/capture.md). Rehearse authentication, third-party prompts, uploads, long-running requests, and destructive actions before recording. Prefer deterministic locators and condition-based waits.

Use [scripts/capture_demo.mjs](scripts/capture_demo.mjs) when a JSON-driven Playwright run fits the product. Copy [assets/capture-plan.example.json](assets/capture-plan.example.json), keep local credentials out of the file, and run:

```bash
npm install
node scripts/capture_demo.mjs path/to/capture-plan.json
```

Capture a clean master with a small amount of handle at the beginning and end. Close the browser context before reading the video because Playwright finalizes recordings on context closure.

### 4. Finish the edit

Read [references/editing.md](references/editing.md). Remove loading frames, failed attempts, idle waits, accidental pointer motion, notification popups, and repeated content. Keep UI animation natural and scrolling smooth.

Use [scripts/finish_video.py](scripts/finish_video.py) for the common finishing pass: trim, crop, scale, pad, fade, burn styled captions, crossfade-loop music, mix source audio, and export an H.264/AAC MP4. Copy [assets/finish-plan.example.json](assets/finish-plan.example.json), then run:

```bash
python scripts/finish_video.py path/to/finish-plan.json
```

For project-specific motion that exceeds the configuration schema, generate an explicit FFmpeg filter graph or use the user's installed editor. Preserve the same source, timing plan, and QA requirements.

### 5. Validate and inspect

Read [references/quality.md](references/quality.md). Run the technical validator with the delivery constraints:

```bash
python scripts/probe_video.py final.mp4 --min-width 1920 --require-audio --max-duration 300
```

Then inspect contact-sheet frames or screenshots at the opening, ending, captions, transitions, and every major feature. Re-export when text clips, a crop cuts navigation awkwardly, overlays touch the safe edge, audio restarts abruptly, the first frame shows loading, or the last frame ends without a clean hold or fade.

## Deliverables

Return only files that help the user continue:

- the final delivery MP4;
- the raw master when requested or when the user plans further editing;
- the capture and finish plans needed to reproduce the result;
- the music or asset provenance record;
- a short validation summary with duration, dimensions, codecs, audio, and any deliberate limitations.

Do not leave obsolete renders, extracted frames, browser profiles, plaintext credentials, or cached third-party media in the project.
