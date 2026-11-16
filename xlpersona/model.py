import torch

MODEL = "CohereLabs/tiny-aya-global"


def load(name: str = MODEL, device: str = "cuda", smoke: bool = False, dtype=None):
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(name)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    if smoke:
        cfg = AutoConfig.from_pretrained(name)
        cfg.num_hidden_layers, cfg.hidden_size, cfg.intermediate_size = 4, 64, 128
        cfg.num_attention_heads, cfg.num_key_value_heads = 4, 2
        if hasattr(cfg, "head_dim"):
            cfg.head_dim = 16
        cfg.layer_types = ["sliding_attention"] * 3 + ["full_attention"]
        torch.manual_seed(0)
        model = AutoModelForCausalLM.from_config(cfg)
    else:
        model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype or torch.bfloat16)
    return tok, model.to(device).eval()


def chat_text(tok, prompt: str, reply: str | None = None) -> str:
    if reply is None:
        return tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True)
    return tok.apply_chat_template([{"role": "user", "content": prompt}, {"role": "assistant", "content": reply}],
                                   tokenize=False)


def position_ids(mask):
    return (mask.long().cumsum(-1) - 1).clamp(min=0)


def encode(tok, texts, device="cpu"):
    enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(device)
    enc["position_ids"] = position_ids(enc["attention_mask"])
    return enc


def _dev(model):
    return next(model.parameters()).device


def generate(tok, model, prompts, bs=64, max_new=160):
    outs = []
    for i in range(0, len(prompts), bs):
        enc = encode(tok, [chat_text(tok, p) for p in prompts[i:i + bs]], _dev(model))
        with torch.no_grad():
            g = model.generate(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
                               max_new_tokens=max_new, do_sample=False, pad_token_id=tok.pad_token_id)
        outs += tok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    return outs


def run_ids(model, ids, mask, hook=None, sink=None):
    if sink is not None:
        hook.mask, hook.sink, hook.mode = mask.bool(), sink, "sink"
    try:
        with torch.no_grad():
            model.model(input_ids=ids, attention_mask=mask, position_ids=position_ids(mask))
    finally:
        if sink is not None:
            hook.mode = hook.sink = hook.mask = None


def last_ids(model, hook, ids, mask):
    hook.buf, hook.mode = [None] * hook.L, "last"
    try:
        run_ids(model, ids, mask)
    finally:
        hook.mode = None
    return torch.stack(hook.buf, 1)


def mlp_last_ids(model, ids, mask):
    layers = model.model.layers
    buf = [None] * len(layers)
    hs = [l.mlp.down_proj.register_forward_pre_hook(lambda m, a, i=i: buf.__setitem__(i, a[0][:, -1].float().cpu()))
          for i, l in enumerate(layers)]
    try:
        run_ids(model, ids, mask)
    finally:
        for h in hs:
            h.remove()
    return torch.stack(buf, 1)


def _batched(tok, model, texts, bs, fn):
    got = []
    for i in range(0, len(texts), bs):
        enc = encode(tok, texts[i:i + bs], _dev(model))
        got.append(fn(enc["input_ids"], enc["attention_mask"]))
    return torch.cat(got)


def last_resid(tok, model, hook, prompts, bs=64):
    texts = [chat_text(tok, p) for p in prompts]
    return _batched(tok, model, texts, bs, lambda ids, m: last_ids(model, hook, ids, m))


def mlp_last(tok, model, prompts, bs=64):
    texts = [chat_text(tok, p) for p in prompts]
    return _batched(tok, model, texts, bs, lambda ids, m: mlp_last_ids(model, ids, m))


def sink_pass(tok, model, hook, texts, sink, bs=32):
    for i in range(0, len(texts), bs):
        enc = encode(tok, texts[i:i + bs], _dev(model))
        run_ids(model, enc["input_ids"], enc["attention_mask"], hook=hook, sink=sink)
