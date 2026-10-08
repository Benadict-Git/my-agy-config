---
name: verify-against-user-references
description: For visual work, reproduce the user's reference images faithfully and check real screenshots side by side before claiming it looks right
metadata:
  type: feedback
---

When the user supplies reference images for visual work (logos, ASCII art, themes), build from those references directly instead of drawing my own interpretation, and compare the output side by side against them and against a real on-screen capture before reporting success.

**Why:** on the Iron Man screensaver the user (a self-described Iron Man fan) rejected ~8 rounds: my hand-drawn stencil read as an "alien face", thresholded photos read as a "ball", and I repeatedly claimed accuracy from text-art dumps without viewing a render. What finally landed was their clean line drawing for shape plus their flat-colour image for colour.
**How to apply:** render to an image and look at it next to the reference every iteration; measure the real display constraints (e.g. terminal grid via `stty size`) instead of assuming; ask for or use a clean line-art source when the input is painterly.
