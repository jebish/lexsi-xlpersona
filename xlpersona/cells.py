import json
import os
from pathlib import Path


def _count(path):
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def run_cells(cells, out_dir, fn) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for cell in cells:
        path = out_dir / f"{cell['name']}.jsonl"
        if path.exists() and _count(path) == cell["n"]:
            continue
        rows = fn(cell)
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, path)
