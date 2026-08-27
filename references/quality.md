# Product demo quality gate

Use this reference before delivering any video or after repairing an export.

## Technical gate

Run `scripts/probe_video.py` with explicit constraints. A normal high-resolution demo command is:

```bash
python scripts/probe_video.py final.mp4 \
  --min-width 1920 \
  --require-audio \
  --max-duration 300 \
  --video-codec h264 \
  --audio-codec aac
```

Verify:

- the file opens and contains a video stream;
- dimensions and frame rate match the delivery brief;
- duration is positive and below the ceiling;
- video and audio codecs are compatible with the destination;
- audio sample rate and channel count are expected;
- the output uses a broadly compatible pixel format such as `yuv420p`;
- the MP4 is seekable and starts promptly;
- there are no decode errors in a full null pass when risk warrants it.

For a full decode check:

```bash
ffmpeg -v error -i final.mp4 -f null -
```

## Visual gate

Generate a contact sheet before detailed playback review:

```bash
python scripts/make_contact_sheet.py final.mp4 artifacts/contact-sheet.png --count 12
```

The adjacent JSON manifest records the sampled timestamps. A contact sheet catches global pacing and framing problems quickly, but it does not replace playback around motion, audio joins, or dense screens.

Inspect actual frames, not only metadata. At minimum inspect:

- the first visible product frame;
- the end of the opening fade;
- every section transition;
- the densest dashboard or table;
- each caption style and both top and bottom placement;
- the deepest crop or zoom;
- any mobile or responsive segment;
- the final hold and last frame.

Reject the export when:

- images, fonts, or charts are still loading;
- a crop leaves half a navigation bar or cuts text unintentionally;
- captions touch an edge, overlap controls, or wrap awkwardly;
- text is too small at normal playback size;
- cursor or scrolling motion jitters;
- a click occurs before the viewer sees the target;
- an overlay describes a result that is not visible;
- a transition flashes black or duplicates frames;
- the ending stops abruptly.

## Audio gate

Listen across:

- the opening fade;
- every music loop boundary;
- the loudest musical section;
- any source audio or narration entrance;
- the final fade.

Reject clicks, abrupt restarts, clipping, pumping, silent gaps, or music that masks speech. Check with headphones and ordinary laptop speakers when the video will be viewed online.

## Product truth gate

Confirm that every feature name, action, metric, and output shown exists in the captured product. Verify that test data is clearly non-production when necessary and that no unintended credentials, API keys, personal notifications, or unrelated tabs appear.

For launch and pitch videos, compare every factual claim and proof scene against the production plan. Reject illustrative scenes presented as product evidence, unsupported customer or traction claims, and generated UI that could be mistaken for the real application.

## Delivery gate

Preserve one canonical master with an unambiguous filename. Provide a checksum when files are copied or moved. Keep the editable plan and license record. Remove stale artifacts only after the final copy has been byte-verified.
