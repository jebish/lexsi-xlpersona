from collections import Counter

from make_ablated import check_prompts, public_directions


def test_check_prompts_are_persona_find_in_en_hi_ne(rows, templates):
    ps = check_prompts(rows, templates, n=20, seed=0)
    assert len(ps) == 20 and sorted(Counter(p.cond for p in ps).values()) == [6, 7, 7]
    assert all(p.template in {"t0", "t1", "t2", "t3"} and p.split == "find" and p.harmful for p in ps)
    assert [p.text for p in ps] == [p.text for p in check_prompts(rows, templates, n=20, seed=0)]


def test_public_directions_cover_every_condition_pooled_and_random(fake_D):
    from xlpersona.conditions import CONDITIONS

    pub = public_directions(fake_D)
    assert set(pub) == {"unit", "diff", "tau", "lstar", "window"}
    assert set(pub["unit"]) == set(pub["tau"]) == set(CONDITIONS) | {"pooled", "rand"}
    assert set(pub["diff"]) == set(CONDITIONS) | {"pooled"}
    assert pub["lstar"] == 1 and pub["window"] == [0, 1, 2]
