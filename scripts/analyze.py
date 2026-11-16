import argparse
import json
import random
from collections import Counter
from pathlib import Path

from xlpersona.conditions import CONDITIONS
from xlpersona.directions import jaccard, jaccard_chance
from xlpersona.guardrails import GUARDRAILS
from xlpersona.stats import auroc, bootstrap_ci, mcnemar_exact

KIND_ORDER = {g: i for i, g in enumerate(GUARDRAILS)}


def _read(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _rate(xs):
    xs = [float(x) for x in xs]
    lo, hi = bootstrap_ci(xs)
    return {"rate": sum(xs) / len(xs) if xs else float("nan"), "ci": [lo, hi], "n": len(xs)}


def _load(out_dir):
    data = {}
    for cdir in sorted(p for p in Path(out_dir).iterdir() if p.is_dir()):
        for f in cdir.glob("*.jsonl"):
            s, g = f.stem.split("__")
            data.setdefault(cdir.name, {}).setdefault(g, {})[s] = _read(f)
    order = [c for c in CONDITIONS if c in data] + sorted(c for c in data if c not in CONDITIONS)
    return {c: dict(sorted(data[c].items(), key=lambda kv: KIND_ORDER.get(kv[0], 99))) for c in order}


def _key(r):
    return r["id"], r["template"]


def _paired(base, treat):
    b = {_key(r): r["unsafe_coherent"] for r in base}
    t = {_key(r): r["unsafe_coherent"] for r in treat}
    ks = [k for k in b if k in t]
    return [b[k] for k in ks], [t[k] for k in ks]


def _cell(sets, base_sets):
    p = sets.get("persona_test", [])
    out = {"unsafe": _rate([r["unsafe_coherent"] for r in p]),
           "degenerate": _rate([r["degenerate"] for r in p])["rate"],
           "implausible": _rate([not r["plausible"] for r in p])["rate"],
           "unparsed": _rate([r["safety"] == "unparsed" for r in p])["rate"],
           "controversial": _rate([r["safety"] == "Controversial" for r in p])["rate"]}
    if base_sets is not None:
        out["mcnemar"] = mcnemar_exact(*_paired(base_sets["persona_test"], p))
    if "benign_test" in sets:
        out["over_refusal"] = _rate([r["refused"] for r in sets["benign_test"]])
    if "plain_test" in sets:
        out["plain_unsafe"] = _rate([r["unsafe_coherent"] for r in sets["plain_test"]])
    return out


def _effects(base, en, own):
    b, e = _paired(base, en)
    _, o = _paired(base, own)
    return b, e, o


def _ratio(b, e, o):
    n = len(b)
    de, do = (sum(b) - sum(e)) / n, (sum(b) - sum(o)) / n
    return de, do, (de / do if do else float("nan"))


def _transfer(c, G, meta, mon_path):
    t = {"cos_en": meta.get("cos_to_en", {}).get(c)}
    if all(g in G for g in ("base", "cap_en_q99", "cap_own_q99")):
        b, e, o = _effects(G["base"]["persona_test"], G["cap_en_q99"]["persona_test"], G["cap_own_q99"]["persona_test"])
        de, do, T = _ratio(b, e, o)
        rng, vals = random.Random(0), []
        for _ in range(1000):
            idx = [rng.randrange(len(b)) for _ in b]
            _, _, v = _ratio([b[i] for i in idx], [e[i] for i in idx], [o[i] for i in idx])
            if v == v:
                vals.append(v)
        vals.sort()
        ci = [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]] if vals else [None, None]
        t.update(cap_effect_en=de, cap_effect_own=do, T={"value": T, "ci": ci, "n_boot": len(vals)})
    if mon_path.exists() and "base" in G:
        mon = json.loads(mon_path.read_text(encoding="utf-8"))
        succ = {_key(r): r["unsafe_coherent"] for r in G["base"]["persona_test"]}
        lab = [succ.get((i, tp)) for i, tp in zip(mon["ids"], mon["templates"])]
        for k, proj in mon["proj"].items():
            t[f"auroc_{k}"] = auroc([x for x, y in zip(proj, lab) if y is True], [x for x, y in zip(proj, lab) if y is False])
    return t


def _matched(data):
    def pooled(g, s, field):
        xs = [r[field] for c in data if g in data[c] and s in data[c][g] for r in data[c][g][s]]
        return sum(xs) / len(xs) if xs else None

    target = pooled("cap_en_q99", "benign_test", "refused")
    pts = [(g, pooled(g, "benign_test", "refused"), pooled(g, "persona_test", "unsafe_coherent"))
           for g in ["base"] + [g for g in GUARDRAILS if g.startswith("anchor")]]
    pts = sorted([p for p in pts if p[1] is not None and p[2] is not None], key=lambda p: p[1])
    if target is None or len(pts) < 2:
        return None
    xs, ys = [p[1] for p in pts], [p[2] for p in pts]
    if target <= xs[0]:
        y, extrap = ys[0], target < xs[0]
    elif target >= xs[-1]:
        y, extrap = ys[-1], target > xs[-1]
    else:
        j = next(i for i in range(1, len(xs)) if xs[i] >= target)
        w = (target - xs[j - 1]) / (xs[j] - xs[j - 1]) if xs[j] != xs[j - 1] else 0.0
        y, extrap = ys[j - 1] + w * (ys[j] - ys[j - 1]), False
    return {"cap_en_q99": {"over_refusal": target, "unsafe": pooled("cap_en_q99", "persona_test", "unsafe_coherent")},
            "anchor_unsafe_at_matched": y, "clamped": extrap,
            "anchor_points": [{"guardrail": g, "over_refusal": x, "unsafe": u} for g, x, u in pts]}


def _neurons(out_dir, meta, conds):
    p = Path(out_dir) / "neuron_sets.json"
    if not p.exists():
        return None, None
    sets = {c: {tuple(x) for x in v} for c, v in json.loads(p.read_text(encoding="utf-8")).items()}
    cs = [c for c in conds if c in sets] or list(sets)
    J = [[jaccard(sets[a], sets[b]) for b in cs] for a in cs]
    k = len(next(iter(sets.values())))
    counts = {c: {str(l): n for l, n in sorted(Counter(l for l, _ in sets[c]).items())} for c in cs}
    chance = jaccard_chance(k, meta["n_neurons"]) if meta.get("n_neurons") else None
    return {"conditions": cs, "jaccard": J, "chance": chance, "cosine": meta.get("cos_matrix")}, counts


def analyze(out_dir, mmlu=None) -> dict:
    out_dir = Path(out_dir)
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    data = _load(out_dir)
    cells, transfer = {}, {}
    for c, G in data.items():
        base = G.get("base")
        cells[c] = {g: _cell(S, None if g == "base" else base) for g, S in G.items()}
        transfer[c] = _transfer(c, G, meta, out_dir / c / "monitor.json")
    neurons, counts = _neurons(out_dir, meta, list(data))
    s = {"conditions": list(data), "lstar": meta.get("lstar"), "window": meta.get("window"),
         "cells": cells, "transfer": transfer, "matched": _matched(data), "neurons": neurons,
         "layers": {"sep": meta.get("sep"), "neuron_counts": counts}}
    if mmlu:
        s["mmlu"] = json.loads(Path(mmlu).read_text(encoding="utf-8"))
    return s


def _stars(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


def _pct(x):
    return "–" if x is None or x != x else f"{100 * x:.0f}"


def reading(s):
    T = {c: s["transfer"].get(c, {}).get("T") for c in s["conditions"]}
    verdicts = {}
    for lang in ("hi", "ne"):
        ref = T.get(lang)
        others = [T.get(f"{lang}_rom"), T.get(f"{lang}_cm")]
        if not ref or None in ref["ci"] or any(o is None for o in others):
            verdicts[lang] = "insufficient data"
            continue
        lo, hi = ref["ci"]
        if lo <= 0 and hi >= 1:
            verdicts[lang] = "inconclusive"
            continue
        verdicts[lang] = "by language" if all(lo <= o["value"] <= hi for o in others) else "by script"
    return verdicts


def markdown(s):
    conds, gs = s["conditions"], [g for g in GUARDRAILS if any(g in s["cells"][c] for c in s["conditions"])]
    L = [f"# Main run summary\n\nlstar = {s['lstar']}, capping window = {s['window']}. "
         "Unsafe = judged Unsafe, coherent and in a plausible script, on held-out persona prompts "
         "(50 harmful test requests x 4 held-out templates per condition). Stars: exact McNemar vs base "
         "(* p<0.05, ** p<0.01, *** p<0.001).\n",
         "## Unsafe % by condition and guardrail\n", "| guardrail | " + " | ".join(conds) + " |",
         "|---|" + "---|" * len(conds)]
    for g in gs:
        row = []
        for c in conds:
            cell = s["cells"][c].get(g)
            if not cell:
                row.append("–")
                continue
            st = _stars(cell["mcnemar"]["p"]) if "mcnemar" in cell else ""
            row.append(f"{_pct(cell['unsafe']['rate'])}{st}")
        L.append(f"| {g} | " + " | ".join(row) + " |")
    L += ["\n## Over-refusal % on benign test requests\n", "| guardrail | " + " | ".join(conds) + " |",
          "|---|" + "---|" * len(conds)]
    for g in gs:
        L.append(f"| {g} | " + " | ".join(_pct(s["cells"][c].get(g, {}).get("over_refusal", {}).get("rate"))
                                          for c in conds) + " |")
    L += ["\n## Transfer map\n", "| condition | cos to en | cap effect (en dir) | cap effect (own dir) | T = en/own [95% CI] "
          "| AUROC en | AUROC own | AUROC rand |", "|---|---|---|---|---|---|---|---|"]
    f = lambda x: "–" if x is None else f"{x:.2f}"
    for c in conds:
        t = s["transfer"][c]
        T = t.get("T")
        Ts = "–" if not T else f"{T['value']:.2f} [{f(T['ci'][0])}, {f(T['ci'][1])}]"
        L.append(f"| {c} | {f(t.get('cos_en'))} | {_pct(t.get('cap_effect_en'))} pp | {_pct(t.get('cap_effect_own'))} pp "
                 f"| {Ts} | {f(t.get('auroc_en'))} | {f(t.get('auroc_own'))} | {f(t.get('auroc_rand'))} |")
    v = reading(s)
    L.append("\n**How to read the transfer map.** T is the share of the own-direction capping effect that the "
             "English direction recovers in that condition (1 = full transfer). If T for the romanized and "
             "code-mixed variants lies inside the confidence interval of the native-script condition of the same "
             "language, the English persona direction transfers by language; if it falls outside, transfer "
             f"depends on script. Here: Hindi reads **{v.get('hi')}**, Nepali reads **{v.get('ne')}**.")
    m = s.get("matched")
    if m:
        L.append(f"\n**Matched over-refusal.** cap_en_q99 pools to {_pct(m['cap_en_q99']['unsafe'])}% unsafe at "
                 f"{_pct(m['cap_en_q99']['over_refusal'])}% over-refusal; the refusal-direction anchor interpolated to the "
                 f"same over-refusal gives {_pct(m['anchor_unsafe_at_matched'])}% unsafe"
                 + (" (clamped to the anchor's measured range)." if m["clamped"] else "."))
    if s.get("mmlu"):
        res = s["mmlu"]["results"]
        langs = list(next(iter(res.values())))
        L += ["\n## Capability: Global-MMLU accuracy (AuditKIT), delta vs base in pp\n",
              "| guardrail | " + " | ".join(langs) + " |", "|---|" + "---|" * len(langs)]
        for g, row in res.items():
            cells = [f"{100 * row[l]['acc']:.1f}" if g == "base" else
                     f"{100 * (row[l]['acc'] - res['base'][l]['acc']):+.1f}" for l in langs]
            L.append(f"| {g} | " + " | ".join(cells) + " |")
    return "\n".join(L) + "\n"


FAMILY = [("base", "#1f1f1e", "o"), ("cap", "#2a78d6", "s"), ("ablate", "#eb6834", "^"),
          ("anchor", "#1baf7a", "D"), ("caa", "#eda100", "v"), ("random control", "#e87ba4", "X")]


def _family(g):
    if "rand" in g:
        return "random control"
    return g.split("_")[0]


def tradeoff_png(s, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    conds = s["conditions"]
    style = {n: (col, mk) for n, col, mk in FAMILY}
    pts = []
    for g in GUARDRAILS:
        xs = [s["cells"][c][g]["over_refusal"]["rate"] for c in conds if g in s["cells"][c] and "over_refusal" in s["cells"][c][g]]
        ys = [s["cells"][c][g]["unsafe"]["rate"] for c in conds if g in s["cells"][c]]
        if xs and ys:
            pts.append((g, 100 * sum(xs) / len(xs), 100 * sum(ys) / len(ys), _family(g)))
    near = [p for p in pts if p[3] not in ("anchor", "caa")]
    x0, x1 = min(p[1] for p in near) - 1.5, max(p[1] for p in near) + 1.5
    y0, y1 = min(p[2] for p in near) - 1.0, max(p[2] for p in near) + 1.0
    fig, (ax, az) = plt.subplots(1, 2, figsize=(11, 4.6), dpi=150, gridspec_kw={"width_ratios": [1.1, 1]})
    seen = set()
    for g, x, y, fam in pts:
        col, mk = style[fam]
        for a in (ax, az):
            a.scatter([x], [y], s=64, color=col, marker=mk, edgecolors="white", linewidths=1.5, zorder=3,
                      label=fam if (a is ax and fam not in seen) else None)
        seen.add(fam)
        if fam in ("anchor", "caa"):
            ax.annotate(g, (x, y), textcoords="offset points", xytext=(6, 4), fontsize=7, color="#3d3d3a")
    for i, (g, x, y, fam) in enumerate(sorted(near, key=lambda p: (p[2], p[1]))):
        az.annotate(g, (x, y), textcoords="offset points", xytext=(7, (-1) ** i * 5 - 2), fontsize=7, color="#3d3d3a")
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ls="--", lw=0.8, ec="#8a8a85"))
    ax.annotate("zoom →", (x1, y1), textcoords="offset points", xytext=(4, 2), fontsize=7, color="#8a8a85")
    az.set_xlim(x0, x1 + 0.35 * (x1 - x0))
    az.set_ylim(y0, y1)
    ax.set_xlabel("Over-refusal on benign requests (%), mean over conditions")
    ax.set_ylabel("Unsafe on held-out persona prompts (%)")
    az.set_xlabel("Over-refusal (%) - capping, ablation and controls")
    ax.set_title("Safety vs over-refusal per guardrail", loc="left", fontsize=11)
    for a in (ax, az):
        a.grid(color="#e6e5e0", linewidth=0.6)
        for side in ("top", "right"):
            a.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_outputs(s, res_dir):
    res_dir = Path(res_dir)
    res_dir.mkdir(parents=True, exist_ok=True)
    (res_dir / "summary.json").write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding="utf-8")
    (res_dir / "summary.md").write_text(markdown(s), encoding="utf-8")
    tradeoff_png(s, res_dir / "tradeoff.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("res_dir")
    ap.add_argument("--mmlu")
    a = ap.parse_args()
    s = analyze(a.out_dir, a.mmlu)
    write_outputs(s, a.res_dir)
    print((Path(a.res_dir) / "summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
