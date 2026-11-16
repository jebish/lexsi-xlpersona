import pytest

from xlpersona.data import build_requests, load_requests, save_requests, select


def _rows(prefix):
    return [{"Goal": f"{prefix} goal {c}{i}", "Category": f"cat{c}", "Behavior": f"b{c}{i}"}
            for c in range(4) for i in range(2)]


@pytest.fixture
def fake_jbb():
    return {"harmful": _rows("harm"), "benign": _rows("ben")}


@pytest.fixture
def fake_tr(fake_jbb):
    from xlpersona.data import split_rows

    tr = {}
    for lang in ["en", "hi", "ne"]:
        tr[lang] = {}
        for key, split in [("H", "harmful"), ("B", "benign")]:
            find, test = split_rows(fake_jbb[split])
            tr[lang][f"{key}_find"] = [(lang + ":" if lang != "en" else "") + r["Goal"] for r in find]
            tr[lang][f"{key}_test"] = [(lang + ":" if lang != "en" else "") + r["Goal"] for r in test]
    return tr


def test_build_requests_split_and_alignment(fake_jbb, fake_tr):
    rows = build_requests(fake_jbb, fake_tr)
    h_find = select(rows, True, "find")
    assert [r["text"]["hi"] for r in h_find] == fake_tr["hi"]["H_find"]
    assert len({r["id"] for r in rows}) == len(rows) == 16
    assert all(set(r["text"]) == {"en", "hi", "ne"} for r in rows)


def test_build_requests_rejects_misaligned_translations(fake_jbb, fake_tr):
    fake_tr["en"]["H_find"] = list(reversed(fake_tr["en"]["H_find"]))
    with pytest.raises(ValueError):
        build_requests(fake_jbb, fake_tr)


def test_save_load_roundtrip(tmp_path, fake_jbb, fake_tr):
    rows = build_requests(fake_jbb, fake_tr)
    save_requests(rows, tmp_path / "r.jsonl")
    assert load_requests(tmp_path / "r.jsonl") == rows
