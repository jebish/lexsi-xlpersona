import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def _tiny(tied: bool = False):
    from transformers import Cohere2Config, Cohere2ForCausalLM

    cfg = Cohere2Config(
        vocab_size=512, hidden_size=64, intermediate_size=128, num_hidden_layers=4,
        num_attention_heads=4, num_key_value_heads=2, head_dim=16,
        layer_types=["sliding_attention", "sliding_attention", "sliding_attention", "full_attention"],
        sliding_window=4096, max_position_embeddings=256, tie_word_embeddings=tied, pad_token_id=0,
    )
    torch.manual_seed(0)
    return Cohere2ForCausalLM(cfg).float().eval()


@pytest.fixture
def tiny():
    return _tiny()


@pytest.fixture
def tiny_tied():
    return _tiny(tied=True)


def left_pad(seqs, pad_id=0):
    T = max(s.shape[1] for s in seqs)
    ids = torch.full((len(seqs), T), pad_id, dtype=torch.long)
    mask = torch.zeros((len(seqs), T), dtype=torch.long)
    for i, s in enumerate(seqs):
        ids[i, T - s.shape[1]:] = s[0]
        mask[i, T - s.shape[1]:] = 1
    return ids, mask


def layer_outputs(model, ids, mask=None):
    from xlpersona.model import position_ids

    mask = torch.ones_like(ids) if mask is None else mask
    outs, hs = [], []
    for layer in model.model.layers:
        hs.append(layer.register_forward_hook(lambda m, a, o: outs.append(o.detach().clone())))
    try:
        with torch.no_grad():
            model.model(input_ids=ids, attention_mask=mask, position_ids=position_ids(mask))
    finally:
        for h in hs:
            h.remove()
    return outs


def forward_hidden(model, ids, mask):
    return layer_outputs(model, ids, mask)[-1]


def sink_ids(model, hook, ids, mask, sink):
    from xlpersona.model import run_ids

    run_ids(model, ids, mask, hook=hook, sink=sink)


NEW_CONDS = ["hi_rom", "ne_rom", "hi_cm", "ne_cm"]


@pytest.fixture
def rows():
    from xlpersona.conditions import CONDITIONS

    out = []
    for i in range(200):
        harmful, split = i < 100, ("find" if i % 100 < 50 else "test")
        meta = {c: {"source": "vllm", "gate_failed": i == 3 and c == "hi_cm"} for c in NEW_CONDS}
        if i == 5:
            meta["ne_rom"]["source"] = "manual"
        out.append({"id": f"{'h' if harmful else 'b'}{i:03d}", "harmful": harmful, "split": split,
                    "text": {c: f"{c} text {i}" for c in CONDITIONS}, "meta": meta})
    return out


@pytest.fixture
def templates():
    from xlpersona.conditions import CONDITIONS
    from xlpersona.templates import Template

    ts = {}
    for i, (split, kept) in enumerate([("find", True)] * 4 + [("heldout", True)] * 4 + [("heldout", False)] * 2):
        ts[f"t{i}"] = Template(id=f"t{i}", split=split, style="s", kept=kept,
                               text={c: f"{c} tpl {i} {{request}}" for c in CONDITIONS})
    return ts


@pytest.fixture
def fake_D():
    from xlpersona.conditions import CONDITIONS
    from xlpersona.directions import random_units, unit

    g = torch.Generator().manual_seed(0)
    keys = list(CONDITIONS) + ["pooled"]
    diff = {k: torch.randn(4, 64, generator=g) for k in keys}
    units = {k: unit(v) for k, v in diff.items()}
    units["rand"] = random_units(4, 64)
    window = [0, 1, 2]
    tau = {k: {q: {l: 0.1 for l in window} for q in (0.95, 0.99, 0.999)} for k in units}
    return {"diff": diff, "unit": units, "tau": tau, "lstar": 1, "window": window,
            "refusal_diff": torch.randn(4, 64, generator=g)}
