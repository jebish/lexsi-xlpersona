import json

from select_heldout import apply_selection, pick_top

from xlpersona.templates import heldout_ids, load_templates, save_templates


def test_pick_top():
    rates = {t: {"en": v, "hi": v, "ne": v} for t, v in
             {"author": .5, "grandma": .1, "gm_npc": .4, "opposite_day": .3, "mad_scientist": .3,
              "villain_interview": .2}.items()}
    assert pick_top(rates) == ["author", "gm_npc", "mad_scientist", "opposite_day"]


def test_apply_selection_flips_kept(tmp_path):
    p = tmp_path / "t.json"
    save_templates(load_templates(), p)
    sel = tmp_path / "s.json"
    sel.write_text(json.dumps({"kept": ["author", "gm_npc", "grandma", "mad_scientist"], "rates": {}}))
    apply_selection(sel, p)
    assert sorted(heldout_ids(load_templates(p))) == ["author", "gm_npc", "grandma", "mad_scientist"]
