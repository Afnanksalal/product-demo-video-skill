# Product video strategy and truth model

Read this before scripting a new walkthrough, launch film, or pitch video. Skip it for a narrow edit or export repair.

## Pick one primary job

Do not combine every possible message into one cut.

| Mode | Viewer question | Required beats | Typical duration |
| --- | --- | --- | --- |
| Walkthrough | How does it work? | context, workflow, outcome | 60 to 300 seconds |
| Launch | Why should I care now? | hook, product, proof, CTA | 20 to 75 seconds |
| Pitch | Why is this a valuable business? | problem, solution, product, proof, CTA | 45 to 180 seconds |

A walkthrough is product-led and chronological. A launch film is attention-led and selective. A pitch is argument-led: it must connect a painful situation to a credible mechanism and evidence. Produce separate cuts when two jobs conflict.

## Four truth sources

Maintain four separate facts throughout production:

1. **Product truth**: observed routes, interactions, states, results, limitations, and approved claims.
2. **Story truth**: audience, objective, central promise, objections, CTA, and required beats.
3. **Visual truth**: brand assets, palette, typography, framing rules, references, and asset rights.
4. **Timeline truth**: scene order, exact durations, narration, captions, music beats, and output variants.

Link every proof scene to a product-truth source. A generated visual may explain an idea but cannot prove that a feature works. Never label a recreated interface, motion graphic, mockup, or model-generated clip as observed product behavior.

Copy `assets/production-plan.example.json` and validate it before capture or rendering:

```bash
python scripts/validate_production_plan.py path/to/production-plan.json
```

## Intake without interrogation

Inspect accessible sources first: product URL, repository, supplied footage, brand files, prior script, and authenticated browser state. Ask only for facts that cannot be discovered safely and that materially affect the result.

Lock these decisions:

- audience and one desired viewer action;
- one primary promise and the proof that supports it;
- mode, duration ceiling, destinations, and aspect ratios;
- real-data permissions and product environment;
- logo, colors, font, pronunciation, approved claims, and prohibited claims;
- voiceover, captions, music, cursor, and reference-video preferences.

When the user supplies a reference video, extract transferable direction: pace, shot density, camera grammar, type behavior, transition families, sound-design rhythm, and emotional contour. Do not copy its footage, wording, brand dress, or signature composition.

## Narrative structures

Choose the smallest structure that supports the objective.

### Walkthrough

Current state -> representative input -> real action -> visible result -> evidence or detail -> summary.

### Launch

Outcome hook -> product reveal -> mechanism -> proof montage -> differentiated benefit -> one CTA.

### Pitch

Specific problem -> consequence -> product thesis -> real workflow -> proof or traction -> why now or differentiation -> one ask.

Lead with an observable outcome when possible. Avoid generic openers such as “The future of work is here.” Keep one claim per beat. Show the product while naming the mechanism; do not make viewers memorize abstract setup and wait for proof later.

## Pilot gate

Before producing the entire film, finish the riskiest 8 to 15 seconds at delivery resolution. The pilot should include one real product shot, representative typography, the intended camera move, captions or narration, and music or sound design. Inspect it at normal playback size.

Do not scale production until the pilot proves:

- the UI remains legible after crop and motion;
- the style belongs to the product rather than a generic template;
- the pacing works with the chosen audio;
- the workflow can be captured without invented state;
- the render path is technically reliable.

Fix upstream choices when the pilot fails. Do not hide weak capture with more effects.

## Copy and claims

Use concrete nouns and verbs. Prefer “Import a bank statement and match deposits” over “Unlock seamless financial clarity.” Titles should orient; body copy should explain the change or proof. On-screen copy is not a transcript unless accessibility requirements call for full subtitles.

Maintain a claim ledger for launch and pitch work: claim, source, approved wording, scene, and risk note. Do not manufacture traction, testimonials, customer logos, security certifications, benchmarks, or third-party endorsement.
