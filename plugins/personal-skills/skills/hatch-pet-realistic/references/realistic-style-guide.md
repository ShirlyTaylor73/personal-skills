# Realistic Style Guide

Use this reference for `$imagegen` base and row-strip prompts when the subject is a realistic human.

## Required Positive Anchors

- `photo-realistic`, `photographic quality`, `cinematic lighting`
- `natural skin texture with pores and subtle imperfections`
- `realistic hair strands with individual fiber detail`
- `accurate human anatomy and proportions (head-to-body ratio ~1:7.5)`
- `natural fabric texture and folds`
- `subject framed against neutral plain background for downstream segmentation`

## Tight Pet Framing

- Base image: one complete full-body person fills `92-96%` of the image height.
- Row strips: each invisible `192x208` frame slot contains one complete full-body person.
- Non-running rows: the person fills `90-96%` of each frame height.
- `running`, `running-left`, and `running-right`: the person fills `84-92%` of each frame height, with room for leg and arm extension.
- Keep the full head, hands, and shoes visible. Do not crop hair, fingers, feet, or motion extremes.
- Use tight full-body framing with no extra empty margin. Avoid distant full-body framing.

## Negative Terms

Put these in the prompt negative section:

- `cartoon`, `anime`, `manga`, `chibi`, `cel-shaded`, `flat colors`
- `3d render`, `cgi`, `pixar style`, `plastic skin`
- `illustration`, `painting`, `painterly`, `concept art`
- `oversized head`, `super-deformed proportions`
- `motion lines`, `speech bubbles`, `text overlays`, `watermarks`
- `multiple subjects`
- `shadow on ground`, `floor plane`, `cast shadow under feet`

## Identity and Clothing Lock

After the base image is approved, the parent agent writes `character_lock` with stable identity, outfit, shoes, hair, and lighting details. Every row prompt must preserve those details.

- Do not change outfit, colors, patterns, hair, shoes, glasses, jewelry, or bags.
- Do not add props unless the row action requires them and the prop is named in the row prompt.
- If `waiting` shows a wristwatch, keep the watch style and color consistent across that row.

## Camera and Lighting

- Use a consistent waist-height camera and 50-85mm equivalent lens for non-running rows.
- Use a slightly lower camera only for forward `running` if needed.
- Keep key light direction, intensity, and color temperature consistent across rows.
- Do not use fisheye, wide-angle distortion, extreme low angle, or extreme high angle.
