import json

import pytest

from analyze import analyze

CONDS = ["en", "hi"]


def _write(path, recs):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")


def _persona(cond, g, unsafe_ids):
    return [{"id": f"h{i:03d}", "template": "t", "cond": cond, "guardrail": g, "safety": "Unsafe" if i in unsafe_ids else "Safe",
             "refusal": "No", "degenerate": False, "plausible": True, "unsafe_coherent": i in unsafe_ids,
             "refused": i not in unsafe_ids} for i in range(100)]


def _benign(cond, g, refused_n):
    return [{"id": f"b{i:03d}", "template": None, "cond": cond, "guardrail": g, "safety": "Safe", "refusal": "Yes" if i < refused_n else "No",
             "degenerate": False, "plausible": True, "unsafe_coherent": False, "refused": i < refused_n} for i in range(50)]


@pytest.fixture
def synthetic_out(tmp_path):
    out = tmp_path / "main"
    unsafe = {"base": set(range(50)), "cap_en_q99": set(range(20, 50)), "cap_own_q99": set(range(40, 50))}
    for c in CONDS:
        for g, ids in unsafe.items():
            _write(out / c / f"persona_test__{g}.jsonl", _persona(c, g, ids))
            _write(out / c / f"benign_test__{g}.jsonl", _benign(c, g, {"base": 5, "cap_en_q99": 5, "cap_own_q99": 10}[g]))
        proj = [1.0 if i < 50 else 0.0 for i in range(100)]
        (out / c / "monitor.json").write_text(json.dumps(
            {"lstar": 1, "ids": [f"h{i:03d}" for i in range(100)], "templates": ["t"] * 100,
             "proj": {"en": proj, "own": proj, "rand": [0.5] * 100}}), encoding="utf-8")
    (out / "meta.json").write_text(json.dumps(
        {"lstar": 1, "window": [0, 1, 2], "sep": {c: [0.1, 0.9, 0.2] for c in CONDS}, "cos_to_en": {"en": 1.0, "hi": 0.8},
         "n_neurons": 1000, "cos_matrix": [[1.0, 0.8], [0.8, 1.0]], "conditions": CONDS}), encoding="utf-8")
    (out / "neuron_sets.json").write_text(json.dumps({"en": [[0, 1], [1, 2]], "hi": [[0, 1], [2, 3]]}), encoding="utf-8")
    return out


def test_cells_and_transfer(synthetic_out):
    s = analyze(synthetic_out)
    assert s["cells"]["hi"]["base"]["unsafe"]["rate"] == 0.5
    assert s["cells"]["hi"]["cap_en_q99"]["mcnemar"]["fixed"] == 20
    assert abs(s["transfer"]["hi"]["T"]["value"] - 0.5) < 1e-9


def test_over_refusal_monitor_and_neurons(synthetic_out):
    s = analyze(synthetic_out)
    assert s["cells"]["hi"]["cap_own_q99"]["over_refusal"]["rate"] == 0.2
    assert s["transfer"]["hi"]["auroc_en"] == 1.0 and s["transfer"]["hi"]["auroc_rand"] == 0.5
    assert s["neurons"]["jaccard"][0][1] == pytest.approx(1 / 3)
    assert s["layers"]["neuron_counts"]["hi"] == {"0": 1, "2": 1}


def test_cli_writes_markdown(synthetic_out, tmp_path):
    from analyze import write_outputs

    res = tmp_path / "res"
    write_outputs(analyze(synthetic_out), res)
    md = (res / "summary.md").read_text(encoding="utf-8")
    assert "Transfer map" in md and "hi" in md and (res / "summary.json").exists()


def _T(v, lo, hi):
    return {"T": {"value": v, "ci": [lo, hi]}}


def test_reading_is_inconclusive_when_native_ci_spans_zero_and_one():
    from analyze import reading

    conds = ["hi", "hi_rom", "hi_cm", "ne", "ne_rom", "ne_cm"]
    s = {"conditions": conds, "transfer": {"hi": _T(0.5, -0.3, 1.3), "hi_rom": _T(0.4, 0, 1), "hi_cm": _T(3.0, 0, 5),
                                           "ne": _T(0.9, 0.6, 1.2), "ne_rom": _T(0.1, -0.2, 0.4), "ne_cm": _T(1.0, 0.7, 1.3)}}
    v = reading(s)
    assert v["hi"] == "inconclusive" and v["ne"] == "by script"
    s["transfer"]["ne_rom"] = _T(0.8, 0.5, 1.1)
    assert reading(s)["ne"] == "by language"
