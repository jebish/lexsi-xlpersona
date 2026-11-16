import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

DEFAULT = Path(__file__).resolve().parents[1] / "data" / "templates.json"


@dataclass
class Template:
    id: str
    split: Literal["find", "heldout"]
    style: str
    text: dict[str, str]
    kept: bool


def load_templates(path: str | Path = DEFAULT) -> dict[str, Template]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {i: Template(id=i, **t) for i, t in raw.items()}


def save_templates(ts: dict[str, Template], path: str | Path = DEFAULT) -> None:
    raw = {i: {"split": t.split, "style": t.style, "kept": t.kept, "text": t.text} for i, t in ts.items()}
    Path(path).write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")


def wrap(t: Template, cond: str, request: str) -> str:
    return t.text[cond].replace("{request}", request)


def find_ids(ts: dict[str, Template]) -> list[str]:
    return [i for i, t in ts.items() if t.split == "find"]


def heldout_ids(ts: dict[str, Template], kept_only: bool = True) -> list[str]:
    return [i for i, t in ts.items() if t.split == "heldout" and (t.kept or not kept_only)]
