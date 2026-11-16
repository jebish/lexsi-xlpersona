import csv
import json
from collections import Counter

import pytest

from export_labels import COLUMNS, export_labels
from score_labels import cohen_kappa, score_labels

LABEL_CONDS = ["hi", "ne", "hi_rom", "ne_rom", "hi_cm", "ne_cm"]
GUARDS = ["base", "cap_en_q99", "anchor_1"]


def _rec(cond, g, i, unsafe, degenerate=False):
    return {"id": f"h{i:03d}", "template": "t", "cond": cond, "guardrail": g, "prompt": f"अनुरोध {i}",
            "reply": f"जवाब {cond} {g} {i}", "safety": "Unsafe" if unsafe else "Safe", "refusal": "No" if unsafe else "Yes",
            "degenerate": degenerate, "plausible": True, "unsafe_coherent": unsafe and not degenerate,
            "refused": not unsafe}


@pytest.fixture
def stage2_out(tmp_path):
    out = tmp_path / "main"
    for cond in LABEL_CONDS + ["en"]:
        (out / cond).mkdir(parents=True)
        for g in GUARDS:
            recs = [_rec(cond, g, i, unsafe=i % 2 == 0, degenerate=i >= 36) for i in range(40)]
            (out / cond / f"persona_test__{g}.jsonl").write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    return out


def _read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_export_is_stratified_and_blind(stage2_out, tmp_path):
    sheet, key = tmp_path / "labels" / "s.csv", tmp_path / "labels" / "k.json"
    export_labels(stage2_out, n=150, seed=0, csv_out=sheet, key_out=key)
    assert sheet.read_bytes()[:3] == b"\xef\xbb\xbf"
    rows, k = _read(sheet), json.loads(key.read_text(encoding="utf-8"))
    assert len(rows) == 150 and list(rows[0]) == COLUMNS
    assert "जवाब" in rows[0]["reply"] and all(r["human_safety"] == "" for r in rows)
    assert {r["cond"] for r in rows} == set(LABEL_CONDS)
    strata = Counter((r["cond"], k[r["uid"]]["safety"]) for r in rows)
    assert len(strata) == 12 and set(strata.values()) == {12, 13}
    assert len({r["uid"] for r in rows}) == 150 and set(k) == {r["uid"] for r in rows}
    assert all(not k[r["uid"]]["degenerate"] for r in rows)


def test_export_draws_from_all_guardrails(stage2_out, tmp_path):
    export_labels(stage2_out, n=150, seed=0, csv_out=tmp_path / "s.csv", key_out=tmp_path / "k.json")
    k = json.loads((tmp_path / "k.json").read_text(encoding="utf-8"))
    per_stratum = Counter((v["cond"], v["safety"], v["guardrail"]) for v in k.values())
    assert all(per_stratum[(c, s, g)] >= 4 for c in LABEL_CONDS for s in ("Safe", "Unsafe") for g in GUARDS)


def test_cohen_kappa():
    assert cohen_kappa(["U", "S", "U", "S"], ["U", "S", "U", "S"]) == 1.0
    assert cohen_kappa(["U", "U", "S", "S"], ["U", "S", "U", "S"]) == 0.0
    assert cohen_kappa(["U", "U"], ["U", "U"]) is None


def test_score_by_kind_skips_blank(tmp_path):
    key = {f"u{i}": {"cond": c, "safety": s, "refusal": "No"} for i, (c, s) in enumerate(
        [("hi", "Unsafe"), ("ne", "Safe"), ("hi_rom", "Unsafe"), ("ne_rom", "Safe"), ("hi_rom", "Unsafe"), ("ne_rom", "Safe"),
         ("hi_cm", "Unsafe")])}
    human = {"u0": "U", "u1": "S", "u2": "U", "u3": "U", "u4": "S", "u5": "S", "u6": ""}
    sheet = tmp_path / "s.csv"
    with open(sheet, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for uid, v in key.items():
            w.writerow({"uid": uid, "cond": v["cond"], "prompt": "p", "reply": "r", "human_safety": human[uid],
                        "human_refusal": "N" if human[uid] else ""})
    (tmp_path / "k.json").write_text(json.dumps(key), encoding="utf-8")
    s = score_labels(sheet, tmp_path / "k.json")
    assert s["safety"]["native"] == {"n": 2, "agreement": 1.0, "cohen_kappa": 1.0, "judge_unsafe_rate": 0.5,
                                     "human_unsafe_rate": 0.5}
    assert s["safety"]["rom"]["n"] == 4 and s["safety"]["rom"]["agreement"] == 0.5
    assert s["safety"]["rom"]["cohen_kappa"] == 0.0 and "cm" not in s["safety"]
    assert s["safety"]["overall"]["n"] == 6 and s["low_kappa"] == ["rom"]
    assert s["refusal"]["overall"]["agreement"] == 1.0
