---
name: product-demo-video-skill
description: Create polished product walkthroughs, launch films, and pitch videos from a real application, website, footage, or product brief. Use for product demos, feature reveals, launch promos, investor or sales pitches, browser capture, storyboarding, motion design, voiceover, captions, music, platform variants, and delivery-ready video. Keep real product proof distinct from illustrative visuals.
license: MIT
metadata:
  author: afnanksalal
  version: "2.0.0"
---

# Product Demo Video Skill

Create a concise, credible product film whose story, product claims, visual system, and timeline remain traceable. Use real interactions as proof, designed motion to frame the story, deterministic media tooling for repeatability, and visible plus technical review before delivery.

Do not rebuild the interface in HTML, generate a simulated dashboard, or substitute screenshots for a functioning product unless the user explicitly requests that style. A demo must not imply that a feature or result exists when it was not observed.

## Choose the production mode

- **Walkthrough**: Explain how the product works with a coherent, real end-to-end flow.
- **Launch**: Create a short, attention-led reveal built around one promise, product proof, and CTA.
- **Pitch**: Make an argument from problem to product mechanism, proof, differentiation, and one ask.
- **Capture and finish**: Inspect the product, record the flow, edit, and export without constructed launch scenes.
- **Capture only**: Record clean source footage and preserve it without overlays or music.
- **Finish existing footage**: Skip product inspection only when the supplied recording and edit brief are sufficient.
- **Repair an export**: Probe the file first, change only the defective parts, and preserve the accepted edit decisions.

Read only the references needed for the selected mode:

- For browser inspection, interaction design, authentication, and recording, read [references/capture.md](references/capture.md).
- For trimming, crop and zoom choices, captions, transitions, music, and FFmpeg finishing, read [references/editing.md](references/editing.md).
- For a new walkthrough, launch, or pitch, read [references/strategy.md](references/strategy.md).
- For constructed scenes, reference-led art direction, and motion grammar, read [references/motion.md](references/motion.md).
- For voiceover, beat-aware music, mixing, and sound design, read [references/audio.md](references/audio.md).
- For aspect-ratio variants and platform delivery, read [references/distribution.md](references/distribution.md).
- For technical and visual acceptance checks, read [references/quality.md](references/quality.md).

## Non-negotiable rules

1. Inspect before scripting. Learn the current routes, navigation, visible states, and real feature names from the running product or source. Never invent a tab, endpoint, metric, result, or interaction.
2. Choose one primary viewer job. A walkthrough teaches, a launch creates desire, and a pitch makes a business case. Create separate cuts when those objectives conflict.
3. Use real interactions. Fill fields, choose options, submit forms, wait for results, open details, and verify the visible outcome. Page hopping alone is not a feature demo.
4. Keep proof and illustration distinct. Generated or reconstructed visuals may explain a concept but cannot prove that a feature, result, customer, metric, or integration exists.
5. Treat side effects as real. Do not create accounts, purchases, messages, uploads, or production data unless the user authorized those actions. Use test or sandbox systems when available.
6. Keep secrets outside committed plans. Resolve credentials from environment variables, a permitted password manager, or an existing authenticated browser profile. Redact them from logs and intermediate files unless the user explicitly asks for visible raw footage.
7. Build and approve the riskiest 8 to 15 second pilot before producing every scene. Fix weak source, story, or framing upstream instead of hiding it with effects.
8. Preserve the raw master until the final export passes QA. Write intermediates to a dedicated artifact directory, never over the only source.
9. Keep the runtime within the requested ceiling. Tighten pauses and remove dead time before dropping requested proof.
10. Use properly licensed audio and retain source, author, license, and retrieval information beside the project.
11. Do not claim completion from a render exit code alone. Probe the output and inspect representative frames, including the opening, every transition, dense UI states, captions, deepest crop, and ending.

## Workflow

Copy and maintain this checklist during substantial work:

```text
Demo progress
- [ ] Define delivery constraints
- [ ] Choose walkthrough, launch, or pitch
- [ ] Link claims and scenes to truth sources
- [ ] Inspect the real product
- [ ] Build a timed shot plan
- [ ] Rehearse risky interactions
- [ ] Finish and approve a representative pilot
- [ ] Record a clean raw master
- [ ] Finish picture, captions, and audio
- [ ] Run technical validation
- [ ] Inspect a contact sheet and representative playback windows
- [ ] Preserve source, project metadata, and final export
```

### 1. Define the contract

Read [references/strategy.md](references/strategy.md) for a new production. Determine the audience, one desired viewer action, primary promise, supporting proof, mode, destinations, aspect ratios, resolution, frame rate, maximum duration, voiceover status, caption style, cursor preference, audio source, and whether real data changes are allowed. Infer ordinary defaults when they do not materially change the outcome:

- Product demos: 16:10 or 16:9 landscape, 30 fps, H.264 video, AAC stereo audio.
- High-resolution master: at least 1920 pixels wide; use the user's requested resolution when specified.
- Browser capture: no visible automation chrome, stable viewport, notifications disabled, and cursor decoration off unless requested.
- Silent demo: concise title plus smaller explanatory line for each important action or result.

Copy [assets/production-plan.example.json](assets/production-plan.example.json), replace its example facts, and validate the story before capture:

```bash
python scripts/validate_production_plan.py path/to/production-plan.json
```

### 2. Inspect and map the product

Open the application and enumerate the current navigation, primary workflow, settings, empty states, success states, and responsive behavior. Check source routes when available. Build a feature coverage table with the exact screen, action, expected visible result, truth source, and estimated seconds.

Remove duplicate screens and explanatory marketing copy that does not demonstrate behavior. Do not begin the recording at a mid-flow screen unless the brief explicitly requires it.

### 3. Make the pilot

Finish the most uncertain 8 to 15 seconds at delivery resolution before scaling the production. Include representative product pixels, type, motion, captions or narration, and audio. Inspect it at normal playback size. For designed launch or pitch scenes, read [references/motion.md](references/motion.md).

### 4. Rehearse, then capture

Read [references/capture.md](references/capture.md). Rehearse authentication, third-party prompts, uploads, long-running requests, and destructive actions before recording. Prefer deterministic locators and condition-based waits.

Use [scripts/capture_demo.mjs](scripts/capture_demo.mjs) when a JSON-driven Playwright run fits the product. Copy [assets/capture-plan.example.json](assets/capture-plan.example.json), keep local credentials out of the file, and run:

```bash
npm install
node scripts/capture_demo.mjs path/to/capture-plan.json
```

Capture a clean master with a small amount of handle at the beginning and end. Close the browser context before reading the video because Playwright finalizes recordings on context closure.

### 5. Finish the edit

Read [references/editing.md](references/editing.md). If narration or beat-aware music is present, also read [references/audio.md](references/audio.md). Remove loading frames, failed attempts, idle waits, accidental pointer motion, notification popups, and repeated content. Keep UI animation natural and scrolling smooth.

Use [scripts/finish_video.py](scripts/finish_video.py) for the common finishing pass: trim, crop, scale, pad, fade, burn styled captions, crossfade-loop music, mix source audio, and export an H.264/AAC MP4. Copy [assets/finish-plan.example.json](assets/finish-plan.example.json), then run:

```bash
python scripts/finish_video.py path/to/finish-plan.json
```

For title cards, diagrams, brand choreography, reusable scenes, or layered pitch visuals, use Genmotion. Do not introduce Remotion, HyperFrames, HTML compositions, or reconstructed product interfaces. Run `npx genmotion doctor --json`, author a truth-linked `brief.json`, generate divergent directions with `npx genmotion plan`, validate with `npx genmotion validate --strict`, inspect native frames and preview, then render the accepted composition. Use the bundled FFmpeg finishing path only for capture cleanup, assembly, captions on raw footage, audio finishing, and delivery conformance.

### 6. Validate and inspect

Read [references/quality.md](references/quality.md). Run the technical validator with the delivery constraints:

```bash
python scripts/probe_video.py final.mp4 --min-width 1920 --require-audio --max-duration 300
```

Then inspect contact-sheet frames or screenshots at the opening, ending, captions, transitions, and every major feature. Re-export when text clips, a crop cuts navigation awkwardly, overlays touch the safe edge, audio restarts abruptly, the first frame shows loading, or the last frame ends without a clean hold or fade.

Generate a representative contact sheet and inspect the actual image:

```bash
python scripts/make_contact_sheet.py final.mp4 artifacts/contact-sheet.png --count 12
```

For more than one output format, read [references/distribution.md](references/distribution.md) and derive platform variants from the accepted master.

## Deliverables

Return only files that help the user continue:

- the final delivery MP4;
- the raw master when requested or when the user plans further editing;
- the capture and finish plans needed to reproduce the result;
- the truth-linked production plan for launch and pitch work;
- the music or asset provenance record;
- a contact sheet and short validation summary with duration, dimensions, codecs, audio, and any deliberate limitations.

Do not leave obsolete renders, extracted frames, browser profiles, plaintext credentials, or cached third-party media in the project.
