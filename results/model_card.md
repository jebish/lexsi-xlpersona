---
license: cc-by-nc-4.0
base_model: CohereLabs/tiny-aya-global
language: [en, hi, ne]
tags: [safety, interpretability, weight-orthogonalization, persona, research-artifact]
---
# tiny-aya-global-persona-ablated

[Tiny Aya Global](https://huggingface.co/CohereLabs/tiny-aya-global) with one residual-stream direction removed
from its weights: the **English persona direction** (difference in means of last-token residuals between
persona-wrapped and plain harmful requests at layer 9 of 36). The direction is projected out of the token
embeddings and of every attention output and MLP down projection, so no layer can write it into the residual
stream. This is equivalent to ablating it at every layer with a hook: in float32, 20 of 20 greedy 64-token
generations on English/Hindi/Nepali persona prompts are identical to hook ablation (all 20 differ from the base
model). Weights are released in bf16.

**This is a research artifact, not a safer model.** Measured on held-out persona jailbreaks (50 harmful
JailbreakBench requests x 4 held-out persona templates per condition, judged by Qwen3Guard-Gen-4B, unsafe =
judged unsafe, coherent and in a plausible script):

| condition | base unsafe % | ablated unsafe % |
|---|---|---|
| English | 45 | 43 |
| Hindi (Devanagari) | 43 | 40 |
| Nepali (Devanagari) | 30 | 25 |
| Hindi romanized | 31 | 34 |
| Nepali romanized | 4 | 6 |
| Hindi code-mixed | 68 | 64 |
| Nepali code-mixed | 32 | 27 |

None of these differences is significant (exact McNemar, p > 0.05). Global-MMLU accuracy changes by -2.0 (en),
-2.0 (hi) and -4.5 (ne) points (n = 200 per language). Removing the direction does not stop persona jailbreaks.
Capping activations along it with the included hook (base model, threshold q99, layers 5-13) cuts jailbreak
success by 8.5 points in English with no over-refusal or MMLU cost, and by 1.3 points pooled over the six Hindi
and Nepali forms (3.8 points when the judge's Controversial verdicts count as unsafe). Capping along each
condition's own direction does at least as well outside English (4.0 points). Judge agreement with a native
speaker (Cohen's kappa, safety): 0.62 Devanagari, 0.63 code-mixed, 0.20 romanized. Full tables:
[persona-jailbreak-7c](https://huggingface.co/datasets/jebish7/persona-jailbreak-7c), `results/summary.json`.

Also in this repo:
* `directions_public.pt`: the persona direction for every condition (`en`, `hi`, `ne`, `hi_rom`, `ne_rom`,
  `hi_cm`, `ne_cm`), the pooled direction and the random control (`unit` per layer; `diff` for all but random),
  capping thresholds `tau` (quantiles 0.95/0.99/0.999 per layer), `lstar` and the capping `window`.
* `hooks.py`: the residual hook (`Resid`, `cap_spec`, `ablate_spec`) used for capping and ablation.
* `check.json`: the hook-equivalence check.

Licence: CC-BY-NC-4.0, inherited from Tiny Aya (Cohere Labs). Attribution: Cohere Labs, Tiny Aya.
