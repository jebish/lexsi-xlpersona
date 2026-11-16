# Script, not language? English persona guardrails in Hindi and Nepali

Persona jailbreaks ("you are DAN", "write as the villain") are among the most reliable attacks on chat models.
Activation-level defences against them, such as capping the residual stream along a "persona direction", are
usually built and evaluated in English. South Asian users write Hindi and Nepali in Devanagari, in romanized form,
and code-mixed with English. We test whether an English persona guardrail protects a multilingual model in these
settings, and whether what transfers follows language or script.

We build a seven-condition benchmark on Tiny Aya Global: English, plus Hindi and Nepali in Devanagari, romanized
and code-mixed. It uses 100 harmful and 100 benign JailbreakBench requests, a find/test split, and 4 held-out
persona templates. Romanized and code-mixed variants were generated with Gemma-3-27B and gated with CuratorKIT.
For each condition we extract a persona direction (difference in means at layer 9 of 36) and compare 14
guardrails on held-out prompts: capping along the English, own-condition, pooled or random direction; directional
ablation; and SafeTune refusal-direction anchoring and contrastive activation addition (CAA). Qwen3Guard judges
the replies, with coherence and script filters; capability is Global-MMLU through AuditKIT. A native speaker
validated the judge (Cohen's kappa 0.62 Devanagari, 0.63 code-mixed, 0.20 romanized) and reviewed the prompts.

Findings. (1) Vulnerability depends on form: code-mixed Hindi is the most jailbreakable condition (68% unsafe vs
45% in English). (2) The English direction recognises persona prompts everywhere: on held-out prompts it recovers
88-96% of each Hindi and Nepali condition's own persona-vs-plain separation (69% for romanized Nepali; a random
direction at most 16%). (3) Capping along it works best in English. It cuts jailbreak success by 8.5 points
[95% CI 3.0, 14.0] in English, with no over-refusal or MMLU cost, and by 1.3 [-1.3, 3.8] pooled over the six
Hindi and Nepali forms (gap 7.3 [1.5, 13.1]). Each form's own direction does at least as well there (4.0 [1.1,
6.8]). Counting the judge's Controversial verdicts as unsafe gives 9.0 in English and 3.8 [1.4, 6.2] elsewhere
(gap 5.3 [0.3, 10.8]). (4) Transfer follows language, not script. Romanized forms share English's script and
align with the English direction least (cosine 0.61 and 0.53, against 0.72 and 0.79 for Devanagari; split-half
reliability 0.99), and romanized Hindi recovers as much separation through it as Devanagari Hindi (0.90 vs 0.89).
(5) Anchoring and CAA cut unsafe rates to 0-18% in every form, but refuse 10-98% of benign requests, lose 7-20
MMLU points and turn up to half of romanized and code-mixed replies into repetition loops. Interpolated to the
same over-refusal as English capping, anchoring leaves 35% unsafe against 34%. (6) Removing the English direction
from the weights does not reduce jailbreaks.

A persona guardrail validated in English gives Hindi and Nepali users a fraction of its English protection, and
code-mixed text is where the model is weakest. Guardrails should be built and tested per language. We release the
benchmark (prompts and judge labels, without model replies), the directions and capping hook for every
condition, and the orthogonalized model.
