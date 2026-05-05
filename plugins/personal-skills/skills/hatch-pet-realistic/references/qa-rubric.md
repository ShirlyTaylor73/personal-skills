# QA Rubric (Realistic Human Pet)

Use this rubric after `finalize_pet_run.py` creates validation JSON and a contact sheet.

## Mechanical Checks

`validate_atlas.py` must pass:

- Atlas size is exactly `1536x1872`.
- Layout is 8 columns x 9 rows, `192x208` per cell.
- Unused cells after each row's final used column are fully transparent.
- Row frame counts match `animation-rows.md`.

## Visual Checks

Review `qa/contact-sheet.png`:

| Dimension | Standard |
| --- | --- |
| Identity | Every visible face reads as the same person: face shape, skin tone, eye color, hair color, hair style, build, and age range stay consistent. |
| Readability | The person is large enough for the pet UI. Non-running rows should fill about `90-96%` of frame height; running rows should fill about `84-92%`. |
| Transparency | Hair edges have no obvious background color, hard rectangular cuts, or large missing sections. |
| Anatomy | Adult realistic proportions, roughly 1:7 to 1:8 head-to-body ratio. No chibi or oversized head. |
| Clothing | Outfit, colors, patterns, shoes, logos, and accessories stay consistent across rows. |
| Style | Photographic skin, fabric texture, realistic light, and no anime, 3D plastic, or painterly look. |
| Motion | `running-right` faces right, `running-left` faces left, `running` faces camera, `jumping` has a readable arc, and `waving` raises the arm above shoulder height. |

## Failure Triage

- Mechanical failure: regenerate or repair the affected row, then rerun `finalize_pet_run.py`.
- Subject too small: regenerate the base or row with tight `192x208` framing and no extra empty margin.
- Edge artifacts: rerun `matte_frames.py --frames-dir <run-dir>/frames_raw --output-dir <run-dir>/frames --qa-dir <run-dir>/qa`; adjust `--feather` only if necessary.
- Identity drift: regenerate the row using `character_lock` and the approved base image as visual truth.
