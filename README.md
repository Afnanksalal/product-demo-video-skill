# Product Demo Video Skill

An open Agent Skill for recording polished product demos from the real application. It combines product inspection, Playwright browser capture, FFmpeg finishing, silent-demo captions, smooth framing, licensed music handling, and technical plus visual QA.

It does not generate a fake HTML recreation of the product. The default workflow records real interactions and preserves the raw master until the finished MP4 passes validation.

## What it handles

- real browser walkthroughs with form input and visible results;
- deterministic capture plans with accessible Playwright locators;
- smooth scrolling, deliberate pacing, and cursor-free recording;
- loading-frame removal, crop, scale, fades, and delivery framing;
- title plus smaller explanatory captions;
- crossfaded background-music loops with provenance requirements;
- H.264/AAC high-resolution exports;
- codec, resolution, duration, audio, decode, and visual QA.

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
$product-demo-video-skill record a five-minute product demo of this application, show real inputs and results, add concise captions and licensed background music, then export and verify a high-resolution MP4.
```

The skill can also activate automatically for product-demo recording and finishing requests.

Templates:

- [`assets/capture-plan.example.json`](assets/capture-plan.example.json)
- [`assets/finish-plan.example.json`](assets/finish-plan.example.json)
- [`assets/music-license-template.md`](assets/music-license-template.md)

Common commands:

```bash
npm install
npx playwright install chromium
node scripts/capture_demo.mjs path/to/capture-plan.json
python scripts/finish_video.py path/to/finish-plan.json
python scripts/probe_video.py final.mp4 --min-width 1920 --require-audio --max-duration 300
```

## Design basis

The repository follows the open [Agent Skills specification](https://agentskills.io/specification), [OpenAI's skill guidance](https://learn.chatgpt.com/docs/build-skills), [Anthropic's Agent Skills guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [Playwright's video recording model](https://playwright.dev/docs/videos), and [FFmpeg's filter documentation](https://ffmpeg.org/ffmpeg-filters.html).

## Security

Skill scripts make no network calls beyond the product URL opened by Playwright. Keep credentials in runtime environment variables or an approved authenticated browser profile. Review any third-party skill before installing it because skills can execute local code with the host agent's permissions.

## License

MIT
