# Voiceover, music, and sound

Read this when the output includes narration, music synchronization, or deliberate sound design.

## Choose the audio leader

- **Voiceover-led**: lock the script and narration timing first; fit visuals to natural speech.
- **Music-led**: detect or mark strong beats and phrase boundaries; place chapter cuts on phrases and internal actions on nearby beats.
- **Interface-led**: preserve meaningful product sounds, then build a restrained bed around the real action.
- **Silent**: design the first frame and captions to carry the story without sound.

Do not force every cut to a beat when it harms comprehension. A musical phrase boundary matters more than constant micro-synchronization.

## Voiceover

Write for speech, not a landing page. Use short clauses, concrete words, and product-specific pronunciation notes. A practical target is 2.2 to 2.7 words per second; more than 3.1 words per second usually requires rewriting. Avoid speeding narration by more than roughly 6 percent. Regenerate or shorten instead.

Record or generate one complete approved read when possible. If narration is produced in segments, keep the same voice, direction, microphone character, sample rate, and room tone. Listen across joins.

The finishing plan accepts a `voiceover` file. It normalizes narration, loops the music bed, and side-chain ducks music under speech:

```json
{
  "voiceover": {
    "path": "voiceover.wav",
    "volume": 1.0,
    "normalize": true,
    "start": 0,
    "ducking": {
      "threshold": 0.03,
      "ratio": 8,
      "attackMs": 20,
      "releaseMs": 320
    }
  }
}
```

Treat these as starting points. Verify intelligibility on headphones and laptop speakers.

## Music

Select for tempo, structure, and brand energy, not genre labels alone. Prefer tracks with a useful opening, clear sections, and an ending that can resolve inside the runtime. Record the title, artist, source URL, license, retrieval date, and modifications.

When a track is shorter than the edit, loop it at phrase boundaries with an equal-power crossfade. A slight tempo fit can hide a nearly exact loop; do not stretch enough to change the character of the track.

## Sound design

Use small sounds to clarify events: click, submit, success, reveal, section transition, or CTA resolve. Do not add a sound to every animation. UI sounds should be short, quiet, and synchronized to visible impact. Avoid copyrighted trademark sounds unless licensed.

## Audio acceptance

Reject clipping, hard loop points, audible edit seams, pumping, excessive noise reduction, music that masks consonants, and a silent tail that feels accidental. For web delivery, a narration-centered mix near -16 LUFS integrated with peaks below -1 dBTP is a useful starting target, not a substitute for listening.
