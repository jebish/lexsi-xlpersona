import copy

import torch

from xlpersona.directions import unit
from xlpersona.hooks import Resid, ablate_spec
from xlpersona.orthogonalize import orthogonalize_


def test_orthogonalized_matches_hook_ablation(tiny):
    r = unit(torch.randn(64)); ids = torch.randint(0, 512, (2, 9))
    hook = Resid(tiny)
    with hook.apply(ablate_spec(r, hook.L)): want = tiny(ids).logits
    m2 = copy.deepcopy(tiny); orthogonalize_(m2, r)
    assert torch.allclose(m2(ids).logits, want, atol=1e-4)


def test_orthogonalize_tied_embeddings(tiny_tied):
    head = tiny_tied.lm_head.weight.detach().clone()
    orthogonalize_(tiny_tied, unit(torch.randn(64)))
    assert torch.equal(tiny_tied.lm_head.weight, head) and not tiny_tied.config.tie_word_embeddings


def test_orthogonalize_changes_output_without_hooks(tiny):
    ids = torch.randint(0, 512, (1, 7))
    ref = tiny(ids).logits
    orthogonalize_(tiny, unit(torch.randn(64)))
    assert not torch.allclose(tiny(ids).logits, ref, atol=1e-3)
