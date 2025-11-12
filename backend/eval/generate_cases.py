import json
import os
import random
random.seed(7)

SRC = os.path.join(os.path.dirname(__file__), "seed.jsonl")
OUT_DIR = os.path.join(os.path.dirname(__file__), "cases")
os.makedirs(OUT_DIR, exist_ok=True)

with open(SRC, "r", encoding="utf-8") as f:
    seeds = [json.loads(line.strip()) for line in f if line.strip()]

cases = []
cases.extend(seeds)


def mutate_name(base, idx): return f"{base}_{idx:02d}"


def variant_from(seed, idx):
    x = json.loads(json.dumps(seed))
    random.shuffle(x["input"]["passages"])
    q = x["input"]["question"]
    q = q.replace("metformin", random.choice(
        ["metformin", "the medicine", "this drug"]))
    x["input"]["question"] = q
    if x["expect"] == "allow" and "answer" in x["input"]:
        ans = x["input"]["answer"]
        if "Rarely" in ans and random.random() < 0.5:
            ans = ans.replace("Rarely", random.choice(
                ["In rare cases", "On rare occasions"]))
        x["input"]["answer"] = ans
    x["name"] = mutate_name(x["name"], idx)
    return x


idx = 1
while len(cases) < 50:
    base = random.choice(seeds)
    cases.append(variant_from(base, idx))
    idx += 1

for i, c in enumerate(cases, 1):
    with open(os.path.join(OUT_DIR, f"case_{i:02d}.json"), "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False)

print(f"Wrote {len(cases)} cases to {OUT_DIR}")
