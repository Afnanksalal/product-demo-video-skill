# Real-product browser capture

Use this reference when the task includes inspecting or recording a live website or web application.

## Contents

- Product inspection
- Shot planning
- Authentication and secrets
- Deterministic interaction
- Smooth movement and pacing
- Playwright capture
- Failure handling

## Product inspection

Inspect the running application before writing the capture plan. Confirm:

- the landing route and authenticated entry route;
- the exact visible navigation labels and route names;
- the primary end-to-end workflow and its prerequisite data;
- which actions mutate data or invoke third parties;
- loading, success, error, empty, and populated states;
- desktop and mobile breakpoints that affect the planned viewport;
- whether the app already contains useful authenticated state.

When source is available, search the route tree and navigation components. Runtime behavior wins when source and deployed behavior differ. Do not rely on a stale script from an earlier version of the product.

## Shot planning

Create a timed table before recording:

| Time | Screen | Real action | Visible proof | Caption |
| --- | --- | --- | --- | --- |
| 00:00 | Landing | Hold briefly, open app | Product identity | Optional |
| 00:08 | Overview | Inspect current state | Real metrics or status | What the viewer is seeing |
| 00:25 | Primary workflow | Enter representative data and submit | Success state or generated record | What changed |
| 01:20 | Result | Open details | Exact output and evidence | Why it matters |

Put overview before transaction unless the user requests a different narrative. Spend time on state changes, not static navigation. For a five-minute ceiling, reserve roughly 15 seconds for opening and ending combined, then allocate the rest by product importance.

## Authentication and secrets

Prefer an existing authenticated browser profile when the user has authorized its use. Otherwise use a test account and resolve credentials at runtime:

```json
{
  "type": "fill",
  "label": "Password",
  "valueFromEnv": "DEMO_PASSWORD"
}
```

Do not write resolved secret values to logs. Do not save storage state into the repository. If the final footage intentionally shows a secret, confirm that this is the user's explicit choice and keep intermediate files private.

## Deterministic interaction

Prefer locator priority in this order:

1. accessible role and visible name;
2. associated form label;
3. stable test id;
4. exact visible text;
5. CSS selector as a last resort.

Wait for observable conditions such as a URL, response, enabled control, visible result, or settled network state. Avoid fixed sleeps for correctness. Use short waits only for editorial pacing after the state is ready.

For custom dropdowns, click the trigger and then the visible option. Do not assume native `select` behavior. For uploads, use the file input directly and verify the filename or imported result.

## Smooth movement and pacing

- Use a consistent viewport and device scale factor.
- Disable browser notifications, password prompts, translation bars, and extension UI.
- Keep pointer decoration off unless the pointer is part of the brief.
- Scroll with an eased animation lasting about 450 to 900 ms, then hold long enough to read the destination.
- Type at a natural but efficient cadence. Fill long opaque IDs instantly; type short human text when visible typing adds meaning.
- Keep a 300 to 800 ms beat after clicks and 800 to 1800 ms on important results.
- Avoid repeated up-and-down scrolling. Frame the next action before performing it.
- Rehearse pages with lazy-loaded images so the recording does not begin on incomplete assets.

## Playwright capture

The bundled `scripts/capture_demo.mjs` reads a JSON action plan and records WebM from a real Chromium context. It supports navigation, role or label based clicks, filling, typing, keyboard input, custom option selection, checks, smooth scrolling, conditional waits, visibility assertions, and timed holds.

Important capture invariants:

- Set viewport and recording size explicitly. Playwright otherwise scales video to a smaller default envelope.
- Await browser-context closure. The recording is not guaranteed complete before that point.
- Use a fresh artifact directory for each take.
- Keep raw footage in the browser-native format. Transcode only in the finishing pass.
- Prefer one continuous take when the flow is stable. Use separate takes when third-party prompts or long jobs make a single take fragile.

Run a plan:

```bash
npm install
npx playwright install chromium
node scripts/capture_demo.mjs artifacts/capture-plan.json
```

## Failure handling

If an action fails, stop the take and report the exact action index, locator, and current URL. Do not continue recording a broken flow. Inspect the page, update the plan, rehearse that segment, and start a fresh take.

Do not bypass CAPTCHA, MFA, payment confirmation, or provider security controls. Let the user complete an interactive challenge when required, or record around the challenge using an approved test mechanism.
