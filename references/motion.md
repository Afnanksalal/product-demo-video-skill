# Motion and art direction

Read this when the video needs designed launch or pitch scenes, a visual refresh, or reference-led motion. For basic browser cleanup, use `editing.md` instead.

## Build a visual system before scenes

Derive a compact system from the product and brand kit:

- one background family, one foreground family, one accent, and semantic status colors;
- one display face and one UI/body face, using actual brand fonts when licensed;
- a spacing unit, corner-radius family, shadow or glow rule, and image treatment;
- one camera grammar and two transition families;
- title, supporting line, annotation, metric, and CTA type scales.

Use product colors as structure, not decoration. Preserve UI color accuracy inside captured footage even when the surrounding film is stylized.

## Directorial verbs

Describe each move by intent and geometry. Useful primitives include:

- **push in** to increase focus on a result;
- **pull back** to reveal system context;
- **track** to follow a workflow across related panels;
- **match cut** between the same object or shape in two states;
- **mask reveal** to introduce a product surface from a brand shape;
- **dip or dissolve** to separate chapters;
- **hard cut on beat** for momentum inside a montage;
- **depth stack** for a small set of related proof cards.

Limit each scene to one dominant move. Coordinate related elements as a group, then add small internal offsets. Independent animation on every object creates noise.

## Camera rules for UI

- Establish the whole screen before the first deep crop.
- Keep the target inside a stable visual quadrant during the move.
- Preserve readable type size at the deepest zoom.
- Never leave half a navbar, browser bar, or panel edge in frame.
- Prefer 1.08x to 1.25x for normal emphasis. Use a deeper crop only for one clear target.
- Let the action complete before moving the camera away.
- Use eased acceleration and deceleration; avoid constant-speed pans.

If a cursor is visible, derive its target from the real element bounds or the capture manifest. Do not eyeball coordinates against a resized screenshot.

## Typography as motion

Typography should arrive in semantic groups. Reveal the claim, then its support, then proof. Keep line lengths short and do not split a phrase at an awkward grammatical boundary. Use scale, opacity, clipping, and position sparingly; a title does not need all four.

For silent films, the first frame must communicate category or outcome without audio. For voiceover films, on-screen type should reinforce the key phrase rather than duplicate every word.

## Avoid generic AI-video patterns

Reject:

- a gradient blob behind every card;
- random glass panels unrelated to the product;
- constant floating, bobbing, or particle noise;
- fake dashboards, fake customer logos, and unreadable generated UI;
- identical spring entrances on every element;
- gratuitous 3D device mockups that make the UI smaller;
- transition packs that call attention to themselves;
- stock “AI brain,” robot, handshake, or person-at-laptop imagery;
- superlatives unsupported by visible proof.

Designed scenes should bridge, frame, or explain real proof. They should not replace it.

## Constructed launch and pitch scenes

Use Genmotion when the brief calls for title cards, brand choreography, diagrams, data visualization, multiple media layers, or reusable aspect-ratio variants. Do not use Remotion, HyperFrames, HTML compositions, or browser capture as a designed-motion renderer.

Call `genmotion_catalog` before assigning motion. Build from named motion recipes and contrastive reference decisions rather than copying a complete template. Every chosen reference must record what the direction borrows, avoids, and transforms.

When the user wants to compare directions or tune exact hierarchy, geometry, motion timing, keyframes, scene holds, transitions, references, or export settings, call `genmotion_studio_start`. Use the Editor's frame-snapped phase clips to retime, trim, remove, and inspect named motion directives against native frames. Import project-specific motion vocabulary through Studio's validated JSON library manager instead of adding renderer code. Treat Studio edits and queued agent requests as authoritative collaboration state. Resolve a request with `genmotion_request_resolve` only after its real Creative IR edit validates and the affected native frames have been inspected.

Keep animation driven by timeline time or frame number so preview, seeking, and render agree. Freeze third-party media locally with provenance. Call `genmotion_validate` in strict mode, render representative native stills with `genmotion_frame`, and use `genmotion_preview_start` before the full encode. Render with `genmotion_render` at high quality or an explicit delivery resolution. High quality must report at least a 1920-pixel long edge; reject a smaller result. After rendering, call `genmotion_probe` and `genmotion_contact_sheet`.

Use FFmpeg directly only for capture cleanup, assembly, raw-footage captions, audio finishing, and final conformance. Genmotion owns constructed scene layout, motion, native rendering, and encoding.
