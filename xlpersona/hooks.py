from contextlib import contextmanager

import numpy as np
import torch


class Resid:
    def __init__(self, model):
        self.layers = model.model.layers
        self.L = len(self.layers)
        self.device = next(model.parameters()).device
        self.spec = self.mode = self.buf = self.mask = self.sink = None
        self.handles = [self.layers[0].register_forward_pre_hook(self._pre, with_kwargs=True)]
        for i, layer in enumerate(self.layers):
            self.handles.append(layer.register_forward_hook(self._post(i)))

    @contextmanager
    def apply(self, spec):
        dev = lambda t: t.to(device=self.device, dtype=torch.float32)
        self.spec = {k: [(op[0], dev(op[1]), *op[2:]) for op in ops] for k, ops in spec.items()} if spec else None
        try:
            yield self
        finally:
            self.spec = None

    def _edit(self, key, h):
        ops = self.spec.get(key) if self.spec else None
        if not ops:
            return None
        x = h.float()
        for op in ops:
            if op[0] == "ablate":
                r = op[1]
                x = x - (x @ r)[..., None] * r
            elif op[0] == "cap":
                r, tau = op[1], op[2]
                x = x - torch.clamp(x @ r - tau, min=0)[..., None] * r
            elif op[0] == "add":
                x = x + op[1]
            else:
                raise ValueError(op[0])
        return x.to(h.dtype)

    def _pre(self, mod, args, kwargs):
        if self.mode is not None:
            return None
        if args:
            h = self._edit(-1, args[0])
            return None if h is None else ((h,) + tuple(args[1:]), kwargs)
        h = self._edit(-1, kwargs["hidden_states"])
        return None if h is None else (args, {**kwargs, "hidden_states": h})

    def _post(self, i):
        def f(mod, args, out):
            h = out[0] if isinstance(out, tuple) else out
            if self.mode == "last":
                self.buf[i] = h[:, -1].float().cpu()
                return None
            if self.mode == "sink":
                self.sink.update(i, h[self.mask].float())
                return None
            e = self._edit(i, h)
            if e is None:
                return None
            return (e,) + tuple(out[1:]) if isinstance(out, tuple) else e
        return f


class ProjSink:
    def __init__(self, R):
        self.R = R
        self.vals = {l: [] for l in R}

    def update(self, i, x):
        if i in self.R:
            self.vals[i].append((x @ self.R[i].to(x.device, x.dtype).T).cpu())

    def quantile(self, q):
        return {l: torch.from_numpy(np.quantile(torch.cat(v).numpy(), q, axis=0)).float()
                for l, v in self.vals.items()}


def ablate_spec(r, L):
    return {k: [("ablate", r)] for k in [-1] + list(range(L))}


def cap_spec(U, tau, window):
    return {l: [("cap", U[l], float(tau[l]))] for l in window}


def add_spec(v, layer):
    return {layer: [("add", v)]}
