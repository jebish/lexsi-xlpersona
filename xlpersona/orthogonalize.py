import torch
from torch import nn


@torch.no_grad()
def _proj_out_rows(W, r):
    Wf = W.float()
    W.copy_((Wf - r[:, None] * (r @ Wf)).to(W.dtype))


@torch.no_grad()
def orthogonalize_(model, r) -> None:
    emb = model.get_input_embeddings()
    if getattr(model.config, "tie_word_embeddings", False):
        model.lm_head.weight = nn.Parameter(emb.weight.detach().clone())
        model.config.tie_word_embeddings = False
        if hasattr(model.config, "get_text_config"):
            model.config.get_text_config().tie_word_embeddings = False
    r = (r / r.norm()).to(device=emb.weight.device, dtype=torch.float32)
    E = emb.weight
    Ef = E.float()
    E.copy_((Ef - (Ef @ r)[:, None] * r).to(E.dtype))
    for layer in model.model.layers:
        for lin in (layer.self_attn.o_proj, layer.mlp.down_proj):
            _proj_out_rows(lin.weight, r)
            if lin.bias is not None:
                b = lin.bias.float()
                lin.bias.copy_((b - (b @ r) * r).to(lin.bias.dtype))
