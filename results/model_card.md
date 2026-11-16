---
license: cc-by-nc-4.0
base_model: CohereLabs/tiny-aya-global
language: [en, hi, ne]
tags: [safety, interpretability, weight-orthogonalization, persona]
---
# tiny-aya-global-persona-ablated

[Tiny Aya Global](https://huggingface.co/CohereLabs/tiny-aya-global) with the English persona direction (layer 9)
projected out of the embeddings, attention outputs and MLP down-projections.

* `directions_public.pt`: persona directions for all seven conditions, pooled and random, with capping thresholds.
* `hooks.py`: residual hook for capping and ablation.

Code: [jebish/lexsi-xlpersona](https://github.com/jebish/lexsi-xlpersona).
Data: [jebish7/persona-jailbreak-7c](https://huggingface.co/datasets/jebish7/persona-jailbreak-7c).
