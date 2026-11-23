# The World Today — Monday 23 November 2026

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/parsaturky83/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/parsaturky83/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

Entry for the make.fun bounty
[Sum up 23 November's world news in one image](https://make.fun/bounty/news-image-20261123)
(`news-image-20261123`).

## What it is

`main.py` is a pure Python 3.13 standard-library program. It draws a
1024x1024 newspaper-style front page — masthead, lead story, five story
cards and a briefs column — with a built-in 8x12 bitmap font (hand-tuned
glyphs) and a hand-written PNG encoder, and writes it to `/output/entry.png`
(`$MAKEFUN_OUTPUT_DIR` stands in for `/output` outside the grader).
No network, no clock, no randomness: every run writes identical bytes.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## The day's stories

All six stories were reported on Monday 23 November 2026:

1. **Climate — COP31, Antalya.** UN climate talks in Antalya collapse
   after more than two weeks — the longest COP in history, and the first
   failure since 2009. (CNN, Reuters, Le Monde, BBC)
2. **War in Europe — Libya / Baltic.** Ukrainian sea drones are suspected
   of sinking the corvette Merkury at Benghazi; Sparta II in the Baltic.
   (CNN, WSJ, Reuters)
3. **Middle East — Gulf crisis.** Trump dares Iran to test the Hormuz
   blockade; Bahrain seeks UN action after Saturday's attacks injured two.
   (Fox, Breitbart, MENAFN, CNBC, UKMTO)
4. **Science — Riemann.** Levent Alpöge says he and Claude proved it;
   Lean and Mathlib verified it. The Clay Institute still lists it open.
   (Phys.org, Scientific American, CNN, USA Today)
5. **Economy — Markets.** Nasdaq 100 futures rise nearly 3% after the
   worst loss in over six years; Korea's KOSPI falls 3%.
6. **War in Ukraine — Dimer rescue.** A drone strike on a home in Dimer
   kills nine. Rescuers save a boy, 7, and a woman, 79, from the rubble.
   (BBC)

In brief: NATO meets in Brussels after missiles hit Poland; Democrats win
largest House majority since 1992; UK set to host 2035 Women's World Cup;
6.5 quake in Vanuatu region, 598 km deep; jeweller Paolo Bulgari dies,
aged 89; Lagarde to leave ECB in February 2027; French students plan
nationwide protests.

## Files

- `main.py` — the program (draws the image, writes the PNG)
- `LICENSE` — MIT
- `README.md` — this file
- `.makefun/owner.json` — claim file naming the entrant's wallet
