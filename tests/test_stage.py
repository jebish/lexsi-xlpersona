from xlpersona.cells import run_cells
from xlpersona.prompts import stage1_prompt_sets, stage2_prompt_sets
from xlpersona.templates import find_ids, heldout_ids


def test_stage1_uses_only_find_split_and_templates(rows, templates):
    prompts = stage1_prompt_sets(rows, templates)
    assert all(p.split == "find" for p in prompts) and {p.template for p in prompts if p.template} == set(find_ids(templates))


def test_stage1_sizes(rows, templates):
    prompts = stage1_prompt_sets(rows, templates)
    plain = [p for p in prompts if p.template is None]
    persona = [p for p in prompts if p.template]
    assert len(plain) == 7 * 100 and len(persona) == 7 * 50 * 4
    assert all(p.harmful for p in persona)


def test_stage2_sets_use_test_split_and_kept_heldout(rows, templates):
    s = stage2_prompt_sets(rows, templates, "hi_rom")
    assert len(s["persona_test"]) == 200 and len(s["benign_test"]) == 50 and len(s["plain_test"]) == 50
    assert {p.template for p in s["persona_test"]} == set(heldout_ids(templates))
    assert all(p.split == "test" and p.cond == "hi_rom" for v in s.values() for p in v)
    assert all(p.harmful for p in s["persona_test"] + s["plain_test"]) and not any(p.harmful for p in s["benign_test"])
    assert s["persona_test"][0].text.startswith("hi_rom tpl") and "hi_rom text" in s["persona_test"][0].text


def test_run_cells_resumes(tmp_path):
    calls = []
    fn = lambda cell: calls.append(cell) or [{"x": 1}] * cell["n"]
    run_cells([{"name": "a", "n": 2}, {"name": "b", "n": 2}], tmp_path, fn)
    (tmp_path / "b.jsonl").unlink(); calls.clear()
    run_cells([{"name": "a", "n": 2}, {"name": "b", "n": 2}], tmp_path, fn)
    assert [c["name"] for c in calls] == ["b"] and len((tmp_path / "a.jsonl").read_text().splitlines()) == 2


def test_run_cells_redoes_short_file(tmp_path):
    (tmp_path / "a.jsonl").write_text('{"x": 1}\n')
    calls = []
    run_cells([{"name": "a", "n": 2}], tmp_path, lambda c: calls.append(c) or [{"x": 1}] * 2)
    assert len(calls) == 1 and not (tmp_path / "a.jsonl.tmp").exists()


def test_stage2_has_30_cells_per_condition(rows, templates):
    from stage2 import build_cells

    cells = build_cells(stage2_prompt_sets(rows, templates, "en"))
    assert len(cells) == 30 and len({c["name"] for c in cells}) == 30
    assert sum(c["n"] for c in cells) == 14 * 200 + 14 * 50 + 2 * 50
