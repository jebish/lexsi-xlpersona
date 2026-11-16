import torch

from .hooks import add_spec
from .io import log
from .model import _dev, chat_text, encode

IMPL: dict[str, str] = {}
META: dict[str, dict] = {}
_CACHE: dict[tuple, dict] = {}


def _fallback(name, fallback, sign, strength, why):
    if fallback is None:
        raise RuntimeError(f"{name}: SafeTune unavailable ({why}) and no fallback given")
    hook, diff, layer = fallback
    IMPL[name] = "fallback"
    META[name] = {"layer": int(layer), "norm": float(diff.norm()), "strength": strength, "why": why}
    return hook.apply(add_spec(sign * strength * diff, layer))


@torch.no_grad()
def _mean_last(model, tok, prompts, layer, bs=32):
    total, n = None, 0
    for i in range(0, len(prompts), bs):
        enc = encode(tok, [chat_text(tok, p) for p in prompts[i:i + bs]], _dev(model))
        hs = model(**enc, output_hidden_states=True).hidden_states[layer + 1][:, -1].float()
        total = hs.sum(0) if total is None else total + hs.sum(0)
        n += hs.shape[0]
    return total / n


def _key(model, a, b):
    return id(model), hash(tuple(a)), hash(tuple(b))


def anchor_calibration(model, tok, harmful, harmless):
    k = ("anchor",) + _key(model, harmful, harmless)
    if k not in _CACHE:
        import safetune.steer as S

        direction, layer, _ = S.extract_refusal_direction(model, tok, harmful, harmless)
        norm = float((_mean_last(model, tok, harmful, layer) - _mean_last(model, tok, harmless, layer)).norm())
        _CACHE[k] = {"direction": direction, "layer": int(layer), "norm": norm}
        log(f"anchor: SafeTune refusal direction at layer {layer}, diff norm {norm:.2f}")
    return _CACHE[k]


def refusal_anchor(model, tok, harmful, harmless, strength, *, fallback=None, calib=None):
    if tok is None:
        return _fallback("anchor", fallback, +1, strength, "no tokenizer")
    try:
        import safetune.steer as S

        c = calib or anchor_calibration(model, tok, harmful, harmless)
        wrapped = S.RefusalDirectionModel(model, direction=c["direction"], mode="steer",
                                          strength=strength * c["norm"], layers=[c["layer"]])
    except Exception as e:
        log(f"anchor: SafeTune failed ({type(e).__name__}: {e}); using hook fallback")
        return _fallback("anchor", fallback, +1, strength, f"{type(e).__name__}: {e}")
    IMPL["anchor"] = "safetune"
    META["anchor"] = {"layer": c["layer"], "norm": c["norm"], "strength": strength}
    return wrapped


def _caa_layer(model):
    from safetune.runner.steer._activation import _default_layers

    band = _default_layers(model, range(14, 19))
    return band[len(band) // 2]


def caa(model, tok, positive, negative, strength, *, fallback=None):
    if tok is None:
        return _fallback("caa", fallback, -1, strength, "no tokenizer")
    try:
        from safetune.runner.steer import CAATrainer

        k = ("caa",) + _key(model, positive, negative)
        if k not in _CACHE:
            layer = _caa_layer(model)
            trainer = CAATrainer(model, tok, target_layers=[layer], pool_method="last_token",
                                 normalize=False, multiplier=1.0)
            wrapped, _ = trainer.calibrate(harmful=positive, harmless=negative)
            vec = next(iter(wrapped.vectors.values())) if hasattr(wrapped, "vectors") else None
            _CACHE[k] = {"wrapped": wrapped, "layer": layer,
                         "norm": float(vec.norm()) if vec is not None else None}
            log(f"caa: SafeTune CAA at layer {layer}, vector norm {_CACHE[k]['norm']}")
        c = _CACHE[k]
        c["wrapped"].strength = float(strength)
    except Exception as e:
        log(f"caa: SafeTune failed ({type(e).__name__}: {e}); using hook fallback")
        return _fallback("caa", fallback, -1, strength, f"{type(e).__name__}: {e}")
    IMPL["caa"] = "safetune"
    META["caa"] = {"layer": c["layer"], "norm": c["norm"], "strength": strength}
    return c["wrapped"]
