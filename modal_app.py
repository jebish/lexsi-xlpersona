import modal

app = modal.App("xlpersona")
vol = modal.Volume.from_name("xlpersona", create_if_missing=True)
secrets = [modal.Secret.from_name("huggingface-secret")]

base = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch>=2.6", "transformers==5.20.2", "accelerate", "sentencepiece", "protobuf",
                 "huggingface_hub", "datasets", "numpy", "scikit-learn")
    .pip_install("safetune==0.1.19", "auditkit==1.1.11", "transformers==5.20.2")
    .add_local_python_source("xlpersona")
    .add_local_dir("data", "/root/data")
    .add_local_dir("scripts", "/root/scripts")
    .add_local_dir("results", "/root/results")
)

vllm_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("vllm", "curatorkit==0.1.27", "openai", "litellm")
    .env({"VLLM_USE_FLASHINFER_SAMPLER": "0"})
    .pip_install("detect-secrets>=1.4", "tenacity>=9.0", "nest-asyncio>=1.6")
    .add_local_python_source("xlpersona")
    .add_local_dir("data", "/root/data")
    .add_local_dir("scripts", "/root/scripts")
)


def _run(script: str, args: list[str]):
    import os
    import subprocess

    env = dict(os.environ, HF_HOME="/vol/hf", XL_OUT="/vol/xl", PYTHONPATH="/root", PYTHONIOENCODING="utf-8")
    tok = env.get("HF_TOKEN") or env.get("HUGGING_FACE_HUB_TOKEN") or env.get("HUGGINGFACE_TOKEN")
    if tok:
        env["HF_TOKEN"] = tok
    try:
        subprocess.run(["python", f"/root/scripts/{script}"] + args, check=True, env=env, cwd="/root")
    finally:
        vol.commit()


@app.function(gpu="L4", image=base, volumes={"/vol": vol}, timeout=3 * 3600, secrets=secrets)
def run_l4(script: str, args: list[str]):
    _run(script, args)


@app.function(gpu="A100", image=base, volumes={"/vol": vol}, timeout=3 * 3600, secrets=secrets,
              max_containers=3)
def run_a100(script: str, args: list[str]):
    _run(script, args)


@app.function(gpu="A100-80GB", image=vllm_image, volumes={"/vol": vol}, timeout=3 * 3600, secrets=secrets)
def run_vllm(script: str, args: list[str]):
    _run(script, args)


CONDS = "en,hi,ne,hi_rom,ne_rom,hi_cm,ne_cm"


@app.function(image=base, volumes={"/vol": vol}, timeout=12 * 3600)
def overnight(conds: str = CONDS):
    import json
    import time
    import traceback

    status = {}

    def mark(name, state, err=None):
        status[name] = {"state": state, "t": time.strftime("%H:%M:%S"), **({"error": err[-2000:]} if err else {})}
        with open("/vol/xl/overnight_status.json", "w") as f:
            json.dump(status, f, indent=1)
        vol.commit()
        print(name, state, flush=True)

    def wait(name, fn):
        mark(name, "running")
        try:
            fn()
            mark(name, "done")
            return True
        except Exception:
            mark(name, "failed", traceback.format_exc())
            return False

    import os

    if os.path.exists("/vol/xl/main/directions.pt"):
        mark("stage1", "skipped: directions.pt exists")
    elif not wait("stage1", lambda: run_a100.remote("stage1.py", [])):
        return status
    calls = {f"stage2_{c}": run_a100.spawn("stage2.py", ["--cond", c]) for c in conds.split(",")}
    calls["mmlu"] = run_a100.spawn("mmlu.py", [])
    calls["ablated"] = run_a100.spawn("make_ablated.py", [])
    for k, fc in calls.items():
        wait(k, fc.get)
    return status


@app.function(image=base, volumes={"/vol": vol}, timeout=3600, secrets=secrets)
def run_cpu(script: str, args: list[str]):
    _run(script, args)


FNS = {"l4": run_l4, "a100": run_a100, "vllm": run_vllm, "cpu": run_cpu}


@app.local_entrypoint()
def main(script: str, args: str = "", gpu: str = "a100", fanout: str = ""):
    if script == "overnight":
        print(overnight.remote())
        return
    fn = FNS[gpu]
    if fanout:
        calls = [(script, args.split() + ["--cond", c]) for c in fanout.split(",")]
        list(fn.starmap(calls))
    else:
        fn.remote(script, args.split())
