import pandas as pd

from export_review import export_review


def test_review_csv_is_excel_safe(tmp_path, rows, templates):
    p = export_review(rows, templates, out=tmp_path / "r.csv")
    assert p.read_bytes()[:3] == b"\xef\xbb\xbf"
    df = pd.read_csv(p, encoding="utf-8-sig")
    assert (df[df.kind == "item"].groupby("cond").size() >= 20).all()


def test_review_includes_failed_manual_and_40_templates(tmp_path, rows, templates):
    df = pd.read_csv(export_review(rows, templates, out=tmp_path / "r.csv"), encoding="utf-8-sig")
    items = df[df.kind == "item"]
    assert ((items.id == "h003") & (items.cond == "hi_cm")).any()
    assert ((items.id == "h005") & (items.cond == "ne_rom")).any()
    tpl = df[df.kind == "template"]
    assert len(tpl) == 40 and not tpl.id.isin(["t8", "t9"]).any()
    assert list(df.columns) == ["kind", "id", "cond", "english", "native", "variant", "ok", "fix", "note"]
    assert not items.duplicated(["id", "cond"]).any()


def test_apply_review_writes_fixes_and_rates(tmp_path, rows, templates):
    from apply_review import apply_review
    from xlpersona.data import load_requests, save_requests
    from xlpersona.templates import load_templates, save_templates

    req, tpl = tmp_path / "requests.jsonl", tmp_path / "templates.json"
    save_requests(rows, req); save_templates(templates, tpl)
    p = export_review(rows, templates, out=tmp_path / "r.csv")
    df = pd.read_csv(p, encoding="utf-8-sig", dtype=str).fillna("")
    df["ok"] = "Y"
    first = df[(df.kind == "item") & (df.cond == "hi_rom")].index[0]
    df.loc[first, ["ok", "fix"]] = ["N", "sahi text"]
    t = df[(df.kind == "template") & (df.cond == "ne_cm")].index[0]
    df.loc[t, ["ok", "fix"]] = ["n", "naya {request} tpl"]
    df.to_csv(p, index=False, encoding="utf-8-sig")
    rep = apply_review(p, requests_path=req, templates_path=tpl)
    assert rep["item"]["hi_rom"]["n"] >= 20 and rep["item"]["hi_rom"]["errors"] == 1
    assert rep["item"]["ne_rom"]["errors"] == 0 and rep["template"]["ne_cm"]["errors"] == 1
    fixed_id = df.loc[first, "id"]
    r = next(r for r in load_requests(req) if r["id"] == fixed_id)
    assert r["text"]["hi_rom"] == "sahi text" and r["meta"]["hi_rom"]["source"] == "manual_review"
    assert load_templates(tpl)[df.loc[t, "id"]].text["ne_cm"] == "naya {request} tpl"


def test_review_samples_native_script_translations(tmp_path, rows, templates):
    df = pd.read_csv(export_review(rows, templates, out=tmp_path / "r.csv"), encoding="utf-8-sig")
    items = df[df.kind == "item"]
    for cond in ("hi", "ne"):
        native = items[items.cond == cond]
        assert len(native) >= 20 and (native.variant == native.native).all()
