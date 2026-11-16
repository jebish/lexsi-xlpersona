import torch
from conftest import layer_outputs

from xlpersona.guardrails import GUARDRAILS, make
from xlpersona.hooks import Resid


def test_guardrail_names_and_spec_shapes(tiny, fake_D):
    assert len(GUARDRAILS) == 14 and GUARDRAILS[0] == "base"
    for g in GUARDRAILS:
        with make(g, "hi_rom", fake_D, Resid(tiny), tiny, None):
            tiny(torch.randint(0, 512, (1, 5)))


def test_cap_own_uses_condition_units(tiny, fake_D):
    hook = Resid(tiny); ids = torch.randint(0, 512, (1, 7))
    with make("cap_own_q99", "ne_cm", fake_D, hook, tiny, None):
        outs = layer_outputs(tiny, ids)
    u = fake_D["unit"]["ne_cm"]
    assert all((outs[l] @ u[l]).max() <= 0.1 + 1e-4 for l in fake_D["window"])


def test_ablate_en_removes_lstar_unit_everywhere(tiny, fake_D):
    hook = Resid(tiny); ids = torch.randint(0, 512, (1, 7))
    with make("ablate_en", "hi", fake_D, hook, tiny, None):
        outs = layer_outputs(tiny, ids)
    r = fake_D["unit"]["en"][fake_D["lstar"]]
    assert all((h @ r).abs().max() < 1e-4 for h in outs)


def test_base_and_exit_leave_model_unchanged(tiny, fake_D):
    hook = Resid(tiny); ids = torch.randint(0, 512, (1, 7))
    ref = layer_outputs(tiny, ids)[-1]
    with make("base", "en", fake_D, hook, tiny, None):
        assert torch.allclose(layer_outputs(tiny, ids)[-1], ref, atol=1e-6)
    with make("anchor_2", "en", fake_D, hook, tiny, None):
        pass
    assert torch.allclose(layer_outputs(tiny, ids)[-1], ref, atol=1e-6)
