import argparse
import shutil
from pathlib import Path

from xlpersona.io import OUT


def main(repo):
    from huggingface_hub import HfApi

    src = OUT / "ablated"
    if not (src / "check.json").exists():
        raise SystemExit("no passing check.json in /vol/xl/ablated; run make_ablated.py first")
    import torch
    from make_ablated import public_directions

    D = torch.load(OUT / "main" / "directions.pt", weights_only=False)
    torch.save(public_directions(D), src / "directions_public.pt")
    shutil.copy("/root/results/model_card.md", src / "README.md")
    shutil.copy("/root/xlpersona/hooks.py", src / "hooks.py")
    api = HfApi()
    api.create_repo(repo, exist_ok=True, private=False)
    api.upload_folder(folder_path=str(src), repo_id=repo, commit_message="persona-ablated Tiny Aya Global")
    print("pushed", f"https://huggingface.co/{repo}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    main(ap.parse_args().repo)
