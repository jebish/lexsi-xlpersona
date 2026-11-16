import re

from xlpersona.templates import find_ids, heldout_ids, load_templates, wrap

LATIN_BANNED = ["VEX", "Malakar", "DAN", "no rules", "no guidelines"]
NATIVE_BANNED = ["मलाकार", "कोई नियम", "कुनै नियम", "दिशानिर्देश", "निर्देशिका"]


def test_every_template_has_one_slot():
    from xlpersona.conditions import CONDITIONS

    for t in load_templates().values():
        for cond, s in t.text.items():
            assert s.count("{request}") == 1, (t.id, cond)
        if t.split == "find" or t.kept:
            assert set(t.text) == set(CONDITIONS), (t.id, sorted(t.text))


def test_find_and_heldout_disjoint_and_sized():
    ts = load_templates()
    assert set(find_ids(ts)) == {"vex", "malakar", "confidant", "dan"}
    assert len(heldout_ids(ts, kept_only=False)) == 6
    assert not set(find_ids(ts)) & set(heldout_ids(ts, kept_only=False))


def test_heldout_avoids_find_markers():
    ts = load_templates()
    for i in heldout_ids(ts, kept_only=False):
        for s in ts[i].text.values():
            assert not any(re.search(rf"\b{re.escape(b)}\b", s, re.I) for b in LATIN_BANNED), i
            assert not any(b in s for b in NATIVE_BANNED), i


def test_wrap_inserts_request():
    t = load_templates()["vex"]
    assert "XYZ" in wrap(t, "en", "XYZ")
