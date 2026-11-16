import torch
from conftest import layer_outputs

from xlpersona.baselines import IMPL, caa, refusal_anchor
from xlpersona.hooks import Resid


def test_fallback_anchor_and_caa_signs(tiny):
    hook = Resid(tiny); v = torch.randn(64); ids = torch.randint(0, 512, (1, 6))
    base = layer_outputs(tiny, ids)[1]
    with refusal_anchor(tiny, None, [], [], 2.0, fallback=(hook, v, 1)):
        up = layer_outputs(tiny, ids)[1]
    with caa(tiny, None, [], [], 2.0, fallback=(hook, v, 1)):
        down = layer_outputs(tiny, ids)[1]
    assert torch.allclose(up - base, 2 * v.expand_as(base), atol=1e-4)
    assert torch.allclose(down - base, -2 * v.expand_as(base), atol=1e-4)
    assert IMPL["anchor"] == IMPL["caa"] == "fallback"


def test_fallback_restores_model(tiny):
    hook = Resid(tiny); v = torch.randn(64); ids = torch.randint(0, 512, (1, 6))
    base = layer_outputs(tiny, ids)[1]
    with refusal_anchor(tiny, None, [], [], 2.0, fallback=(hook, v, 1)):
        pass
    assert torch.allclose(layer_outputs(tiny, ids)[1], base, atol=1e-6)
