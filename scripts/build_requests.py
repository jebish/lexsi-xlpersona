import argparse
import json

from xlpersona.data import DEFAULT, build_requests, counts_line, load_jbb, load_requests, save_requests
from xlpersona.io import ROOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--translations")
    a = ap.parse_args()
    if not a.check:
        tr = json.loads((ROOT / a.translations).read_text(encoding="utf-8"))
        save_requests(build_requests(load_jbb(), tr))
    print(counts_line(load_requests(DEFAULT)))


if __name__ == "__main__":
    main()
