from dataclasses import dataclass

from .conditions import CONDITIONS
from .templates import find_ids, heldout_ids, wrap


@dataclass
class Prompt:
    id: str
    cond: str
    template: str | None
    split: str
    harmful: bool
    text: str


def stage1_prompt_sets(rows, templates) -> list[Prompt]:
    find = [r for r in rows if r["split"] == "find"]
    out = []
    for c in CONDITIONS:
        out += [Prompt(r["id"], c, None, "find", r["harmful"], r["text"][c]) for r in find]
        out += [Prompt(r["id"], c, t, "find", True, wrap(templates[t], c, r["text"][c]))
                for t in find_ids(templates) for r in find if r["harmful"]]
    return out


def stage2_prompt_sets(rows, templates, cond) -> dict[str, list[Prompt]]:
    test = [r for r in rows if r["split"] == "test"]
    harm = [r for r in test if r["harmful"]]
    return {
        "persona_test": [Prompt(r["id"], cond, t, "test", True, wrap(templates[t], cond, r["text"][cond]))
                         for t in heldout_ids(templates) for r in harm],
        "benign_test": [Prompt(r["id"], cond, None, "test", False, r["text"][cond]) for r in test if not r["harmful"]],
        "plain_test": [Prompt(r["id"], cond, None, "test", True, r["text"][cond]) for r in harm],
    }
