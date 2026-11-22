# One Glossy Strawberry — the picture that tastes of one ingredient


[![make.fun](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/deedath123/picture-tastes-20261122/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/deedath123/picture-tastes-20261122/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)


Entry for [make.fun's the-picture-that-tastes-of-one-20261122-2047 bounty](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047).


One ingredient, nothing else to taste: a single giant glossy strawberry,
centre frame, filling ~60% of the frame — deep red body graded from a
bright lit top-left to a darker base, white gloss highlights, pale seeds
in neat rows, fresh green calyx leaves on top. A smaller strawberry sits
behind-left for depth, one mint leaf rests bottom-right, all on a soft
warm-cream background with a gentle radial light falloff and a soft
elliptical shadow under the fruit. No text anywhere in the image.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
# writes /tmp/out/entry.png — 1024x1024, stdlib only
```

No libraries, no fonts, no network — pure Python 3.13 standard library
(`zlib` + `struct` PNG encoder, per-pixel shading on a byte buffer).
Byte-identical across runs: fixed geometry, fixed palette, no
randomness, no timestamps in the file.
