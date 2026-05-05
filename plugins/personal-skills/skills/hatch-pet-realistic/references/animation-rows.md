# Animation Rows (Realistic Human)

The Codex app reads one fixed atlas: 8 columns, 9 rows, 192x208 pixels per cell.

| Row | State | Used columns | Durations |
| --- | --- | ---: | --- |
| 0 | idle | 0-5 | 280, 110, 110, 140, 140, 320 ms |
| 1 | running-right | 0-7 | 120 ms each, final 220 ms |
| 2 | running-left | 0-7 | 120 ms each, final 220 ms |
| 3 | waving | 0-3 | 140 ms each, final 280 ms |
| 4 | jumping | 0-4 | 140 ms each, final 280 ms |
| 5 | failed | 0-7 | 140 ms each, final 240 ms |
| 6 | waiting | 0-5 | 150 ms each, final 260 ms |
| 7 | running | 0-5 | 120 ms each, final 220 ms |
| 8 | review | 0-5 | 150 ms each, final 280 ms |

Unused cells after each row's final used column must be fully transparent.

## Row Purposes

- `idle`: standing loop with subtle breathing, blinking, or a small head turn. Frame 0 and final used frame return to a neutral standing pose.
- `running-right`: side-view run facing right. Use 8 frames: contact, down, passing, high-point, then the opposite step cycle. Arms swing opposite the legs.
- `running-left`: side-view run facing left, generated independently. Do not mirror `running-right`.
- `waving`: front-facing greeting. Use 4 frames: arm rising, peak wave, wrist tilt, arm returning.
- `jumping`: vertical jump. Use 5 frames: knee bend, push-off, peak airborne, landing cushion, settled stance.
- `failed`: disappointment or failure reaction. Use 8 frames: realization, head shake, hands on head, head down, sigh, palms-up shrug, rubbing temple, recovery.
- `waiting`: patient wait loop. Use 6 frames: checking wristwatch, hands in pockets, weight shift, looking into distance, arms folded, return to neutral.
- `running`: front-view run toward camera. Use 6 frames with alternating legs and pumping arms.
- `review`: focused review or thinking loop. Use 6 frames: hand on chin, head tilt, magnifying glass or document, nod, focused gaze, return.

## Identity Lock

Every row prompt starts with `pet_request.json#character_lock`. Preserve identity, face, hair, clothing, shoes, proportions, and lighting across all rows.
