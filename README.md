# Product Demo Video Skill

An open Agent Skill for creating polished product walkthroughs, launch films, and pitch videos. It combines product strategy, truth-linked storyboards, real Playwright browser capture, designed motion, FFmpeg finishing, voiceover ducking, captions, licensed music, multi-format delivery, and technical plus visual QA.

It treats the real product as the proof layer. Designed or generated visuals can frame a story, but they cannot impersonate an observed feature, result, customer, or metric. Raw masters and production facts remain reproducible until the finished video passes review.

## What it handles

- walkthrough, launch, and pitch narrative modes;
- truth-linked production plans and claim discipline;
- pilot-first art direction before full production;
- real browser walkthroughs with form input, visible results, and sanitized action timelines;
- deterministic capture plans with accessible Playwright locators;
- reference-video direction without copying third-party assets;
- smooth scrolling, deliberate pacing, and cursor-free recording;
- loading-frame removal, crop, scale, fades, and delivery framing;
- title plus smaller explanatory captions;
- voiceover normalization with automatic music ducking;
- beat-aware editing and crossfaded background-music loops with provenance requirements;
- designed launch and pitch scenes through an available deterministic timeline engine;
- landscape, vertical, square, and feed-safe delivery guidance;
- automated contact sheets for visual review;
- H.264/AAC high-resolution exports;
- codec, resolution, duration, audio, decode, product-truth, and visual QA.

## Requirements

- Python 3.10 or newer
- Node.js 20 or newer for browser capture
- FFmpeg and ffprobe on `PATH`
- Chromium installed through Playwright for browser capture

## Install for Codex

Clone the repository into your user skills directory:

```bash
git clone https://github.com/Afnanksalal/product-demo-video-skill.git ~/.agents/skills/product-demo-video-skill
```

Codex also discovers repository-scoped skills placed at `.agents/skills/product-demo-video-skill`. Restart Codex only if the skill does not appear automatically.

PowerShell:

```powershell
git clone https://github.com/Afnanksalal/product-demo-video-skill.git "$HOME\.agents\skills\product-demo-video-skill"
```

## Install for Claude Code

Clone it as a personal skill:

```bash
git clone https://github.com/Afnanksalal/product-demo-video-skill.git ~/.claude/skills/product-demo-video-skill
```

For one project, place it at `.claude/skills/product-demo-video-skill` instead.

PowerShell:

```powershell
git clone https://github.com/Afnanksalal/product-demo-video-skill.git "$HOME\.claude\skills\product-demo-video-skill"
```

## Use

Invoke it explicitly:

```text
$product-demo-video-skill create a 60-second launch film from this real application. Show the primary workflow and visible proof, match the product brand, add concise captions and licensed music, then export and verify 16:9 and 9:16 masters.
```

The skill can also activate automatically for product-demo recording and finishing requests.

Templates:

- [`assets/production-plan.example.json`](assets/production-plan.example.json)
- [`assets/capture-plan.example.json`](assets/capture-plan.example.json)
- [`assets/finish-plan.example.json`](assets/finish-plan.example.json)
- [`assets/music-license-template.md`](assets/music-license-template.md)

Common commands:

```bash
npm install
npx playwright install chromium
python scripts/validate_production_plan.py path/to/production-plan.json
node scripts/capture_demo.mjs path/to/capture-plan.json
python scripts/finish_video.py path/to/finish-plan.json
python scripts/probe_video.py final.mp4 --min-width 1920 --require-audio --max-duration 300
python scripts/make_contact_sheet.py final.mp4 artifacts/contact-sheet.png --count 12
```

## Production architecture

- **Strategy layer:** chooses walkthrough, launch, or pitch and links each proof beat to a real source.
- **Capture layer:** records the actual product with deterministic interactions and a sanitized timing manifest.
- **Design layer:** uses product-native art direction and a deterministic timeline engine when constructed scenes are needed.
- **Finish layer:** handles trimming, framing, captions, voiceover, music, fades, and delivery encoding with FFmpeg.
- **Review layer:** validates media constraints, decodes the full export when needed, and produces a contact sheet for visual inspection.

## Design basis

The repository follows the open [Agent Skills specification](https://agentskills.io/specification), [OpenAI's skill guidance](https://learn.chatgpt.com/docs/build-skills), [Anthropic's Agent Skills guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [Playwright's video recording model](https://playwright.dev/docs/videos), and [FFmpeg's filter documentation](https://ffmpeg.org/ffmpeg-filters.html).

The production model was benchmarked against [Oil Motion](https://github.com/oil-oil/oil-motion), [SaaS Product Demo Video](https://github.com/noamdorr/saas-product-demo-video), [Product Launch Video Skill](https://github.com/memex-lab/product-launch-video-skill), and [Super Video Maker Skill](https://github.com/Bomx/super-video-maker-skill). Their strongest ideas informed pilot gating, reference breakdowns, beat-aware pacing, designed launch scenes, delivery variants, and stricter proof review; this implementation and its scripts remain original.

## Security

Skill scripts make no network calls beyond the product URL opened by Playwright. Keep credentials in runtime environment variables or an approved authenticated browser profile. Review any third-party skill before installing it because skills can execute local code with the host agent's permissions.

## License

MIT
