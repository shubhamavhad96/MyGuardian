from worker.worker import evaluate_payload  # import directly
import json
import sys
import glob
import os
from typing import Tuple
# add backend/ to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


GREEN = "\033[92m"
RED = "\033[91m"
YEL = "\033[93m"
RST = "\033[0m"


def run_one(path: str) -> Tuple[bool, str, str]:
    data = json.load(open(path, "r", encoding="utf-8"))
    expect = data["expect"].lower().strip()
    payload = data["input"]
    res = evaluate_payload(payload)
    got = res["decision"]
    ok = (got == expect)
    return ok, expect, got


def main():
    files = sorted(glob.glob(os.path.join(
        os.path.dirname(__file__), "goldens", "*.json")))
    if not files:
        print(RED + "No golden files found." + RST)
        sys.exit(1)

    passed = 0
    print("\nGolden Tests\n------------")
    for f in files:
        ok, expect, got = run_one(f)
        name = json.load(open(f, "r", encoding="utf-8"))["name"]
        mark = GREEN + "PASS" + RST if ok else RED + "FAIL" + RST
        print(f"{mark} | {os.path.basename(f)} | {name} | expect={expect} got={got}")
        if ok:
            passed += 1

    total = len(files)
    print("\nSummary")
    print("-------")
    color = GREEN if passed == total else (YEL if passed >= total//2 else RED)
    print(color + f"{passed}/{total} passed" + RST)
    sys.exit(0 if passed == total else 2)


if __name__ == "__main__":
    main()
