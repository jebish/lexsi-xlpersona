import torch
import torch.nn.functional as F
from conftest import forward_hidden, layer_outputs, left_pad, sink_ids

from xlpersona.hooks import ProjSink, Resid, ablate_spec, add_spec, cap_spec
from xlpersona.model import last_ids, mlp_last_ids


def test_no_spec_is_identity(tiny):
    ids = torch.randint(0, 512, (2, 9))
    ref = tiny(ids).logits
    Resid(tiny)
    assert torch.allclose(tiny(ids).logits, ref, atol=1e-6)


def test_ablate_removes_direction_everywhere(tiny):
    hook = Resid(tiny)
    r = F.normalize(torch.randn(64), dim=0)
    with hook.apply(ablate_spec(r, hook.L)):
        outs = layer_outputs(tiny, torch.randint(0, 512, (2, 9)))
    assert all((h @ r).abs().max() < 1e-4 for h in outs)


def test_cap_bounds_projection_in_window(tiny):
    hook = Resid(tiny)
    U = F.normalize(torch.randn(4, 64), dim=-1)
    with hook.apply(cap_spec(U, {1: 0.1, 2: 0.1}, [1, 2])):
        outs = layer_outputs(tiny, torch.randint(0, 512, (2, 9)))
    assert (outs[1] @ U[1]).max() <= 0.1 + 1e-4 and (outs[2] @ U[2]).max() <= 0.1 + 1e-4


def test_add_shifts_layer_output(tiny):
    hook = Resid(tiny)
    v = torch.randn(64)
    ids = torch.randint(0, 512, (1, 6))
    base = layer_outputs(tiny, ids)[1]
    with hook.apply(add_spec(v, 1)):
        moved = layer_outputs(tiny, ids)[1]
    assert torch.allclose(moved - base, v.expand_as(base), atol=1e-4)


def test_apply_clears_spec(tiny):
    hook = Resid(tiny)
    with hook.apply(add_spec(torch.ones(64), 0)):
        assert hook.spec is not None
    assert hook.spec is None


def test_padded_equals_unpadded(tiny):
    a, b = torch.randint(1, 512, (1, 5)), torch.randint(1, 512, (1, 9))
    batch, mask = left_pad([a, b], pad_id=0)
    hb = forward_hidden(tiny, batch, mask)
    assert torch.allclose(hb[0, -5:], forward_hidden(tiny, a, torch.ones_like(a))[0], atol=1e-4)


def test_sink_ignores_pads(tiny):
    a, b = torch.randint(1, 512, (1, 5)), torch.randint(1, 512, (1, 9))
    R = {1: F.normalize(torch.randn(2, 64), dim=-1)}
    padded, alone = ProjSink(R), ProjSink(R)
    hook = Resid(tiny)
    batch, mask = left_pad([a, b], pad_id=0)
    sink_ids(tiny, hook, batch, mask, padded)
    for x in (a, b):
        sink_ids(tiny, hook, x, torch.ones_like(x), alone)
    assert torch.cat(padded.vals[1]).shape[0] == 14
    assert torch.allclose(padded.quantile(0.9)[1], alone.quantile(0.9)[1], atol=1e-4)


def test_last_ids_matches_layer_outputs(tiny):
    hook = Resid(tiny)
    a, b = torch.randint(1, 512, (1, 5)), torch.randint(1, 512, (1, 9))
    batch, mask = left_pad([a, b])
    got = last_ids(tiny, hook, batch, mask)
    outs = layer_outputs(tiny, batch, mask)
    assert got.shape == (2, 4, 64)
    assert torch.allclose(got[:, 2], outs[2][:, -1], atol=1e-5)


def test_mlp_last_ids_shape_and_value(tiny):
    ids = torch.randint(1, 512, (2, 6))
    seen = []
    h = tiny.model.layers[3].mlp.down_proj.register_forward_pre_hook(lambda m, a: seen.append(a[0][:, -1].clone()))
    got = mlp_last_ids(tiny, ids, torch.ones_like(ids))
    h.remove()
    assert got.shape == (2, 4, 128)
    assert torch.allclose(got[:, 3], seen[0], atol=1e-6)
