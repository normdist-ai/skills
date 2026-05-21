# Seed Management Strategy

## Why Seeds Matter

Seeds are not just "random starting points" — each seed has an innate **theme/flavor** that persists across prompts:

- **Color palette** — warm tones, cool tones, muted, vivid
- **Composition & cropping** — headshot, waist-up, full body tendency
- **Default clothing** — some seeds consistently generate red/blue/dark clothing regardless of prompt
- **Background structure** — indoor/outdoor bias, sky presence, geometric patterns

Changing a seed by ±1 produces a completely different image. There is no "continuity" between adjacent seed numbers.

### Academic Validation

arXiv paper "Discovering Secret Seeds in Text-to-Image Diffusion Models" (2405.14828) analyzed 46 million images:

- A classifier can predict which seed produced an image with **99.9% accuracy** from 1,024 candidates
- **"Golden seeds" are real**: ~65 seeds consistently produce superior FID scores and human preference ratings across diverse prompts
- Seed quality rankings **generalize across prompts** — a golden seed for prompt A tends to also be golden for prompt B
- Seeds also cluster by style (grayscale tendency, sky regions, warm tones) and composition (object placement)

## Seed Selection Workflow (Community Best Practice)

From Reddit (u/wonderflex, u/anonymous seed tutorial author):

1. **Batch generate** — same prompt, 20-50 different seeds (A1111 XYZ script or ComfyUI batch)
2. **Observe themes** — note each seed's innate color, cropping, default clothing, background
3. **Select compatible seed** — pick the seed whose theme already matches your target ("choose the stone that already has your sculpture in it")
4. **Refine on chosen seed** — modify prompt while keeping the seed fixed; the theme persists

### Key Insight: Prompt-Seed Compatibility

> "If you want an awesome dragon, it's easier if you start with a seed that might contain one."

- Low CFG (1-2): Seed theme dominates. Prompt has minimal influence.
- Medium CFG (4): Balanced. Seed theme visible but prompt drives content. **← Our default CFG=4.0 is here.**
- High CFG (15+): Prompt forces output. Seed theme nearly invisible but artifacts increase.

This means at our CFG=4.0, the seed's innate theme still significantly influences the result. Good seed selection matters.

## Seed Pool Design

### File: `prompts/good-seeds.txt` (to be created)

```
# One seed per line, optional scene tag after comma
86522080        # default — verified across all scenes, 30-image stability test
474416506       # early verified
# Add more after batch testing:
# seed1,boulevard    # good for boulevard scene
# seed2,cafe         # good for cafe scene
```

### selfie-v3.py Logic

```
--seed N          → use exactly seed N
(no flag)         → random pick from good-seeds.txt
--random-seed     → true random (torch randint, for exploration)
```

### Adding New Seeds

1. Run `python selfie-v3.py --random-seed` 20 times with same prompt
2. User picks favorites → note seed numbers from output filenames (`HMM-v3-{date}-{seed}.png`)
3. Append to good-seeds.txt

## Verified Seeds

|| Seed | Notes | Verified Scenes | Added |
||------|-------|----------------|--------|
|| 86522080 | Default seed,构图稳定，手部表现好 | All (30-image test) | 2026-05-21 |

> **注意**：arXiv 2405.14828 论文的 golden seeds（~65 for SD2.0, ~67 for SDXL Turbo）未公开具体列表。
> 它们是针对 MS-COCO prompts + SD 2.0/SDXL Turbo 的，跟我们的模型和人像场景不同，不能直接套用。

## Sources

- Reddit: [Seed Tutorial](https://www.reddit.com/r/StableDiffusion/comments/xhsf8c/) — seed themes, CFG interaction
- Reddit: [Seed Selection Tutorial](https://www.reddit.com/r/StableDiffusion/comments/x8szj9/) — batch selection workflow, "flavor" concept
- Civitai: [List of Useful Seeds](https://civitai.com/articles/14921/) — community seed collection
- arXiv: [2405.14828](https://arxiv.org/html/2405.14828v2) — "Discovering Secret Seeds", 46M image analysis, golden seeds
- Chris McCormick: [Steps and Seeds](https://mccormickml.com/2023/01/11/steps-and-seeds/) — seed mechanics
