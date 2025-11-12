from worker.worker import evaluate_payload
import os
import json
import glob
import statistics
import sys
import csv
import argparse
from collections import defaultdict
from datetime import datetime

# Add backend/ to path
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)


def load_cases_json(path):
    files = sorted(glob.glob(os.path.join(path, "*.json")))
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            yield os.path.basename(fp), json.load(f)


def load_cases_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            name = f"case_{idx:03d}"
            try:
                passages = json.loads(row["passages"]) if row["passages"] else []
            except (json.JSONDecodeError, KeyError):
                # Fallback: try to parse as literal Python list
                import ast
                try:
                    passages = ast.literal_eval(row.get("passages", "[]"))
                except:
                    passages = []
            case = {
                "name": f"{row.get('domain', 'unknown')}_{idx}",
                "expect": row["expect"],
                "input": {
                    "question": row["question"],
                    "answer": row["answer"],
                    "passages": passages
                }
            }
            yield name, case


def generate_markdown_report(results, policy_presets=None):
    md = ["# RAG Guardrail Evaluation Report\n"]
    md.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total = results["total"]
    passed = results["passed"]
    md.append("## Summary\n\n")
    md.append(f"- **Total Cases**: {total}\n")
    md.append(f"- **Passed**: {passed} ({passed/total*100:.1f}%)\n")
    md.append(f"- **Failed**: {total-passed} ({(total-passed)/total*100:.1f}%)\n\n")
    
    md.append("## Metrics\n\n")
    md.append(f"- **Faithfulness (avg)**: {results['faith_avg']:.3f}\n")
    md.append(f"- **Coverage (avg)**: {results['cov_avg']:.3f}\n")
    md.append(f"- **Toxicity (avg)**: {results['tox_avg']:.3f}\n\n")
    
    md.append("## Decision Breakdown\n\n")
    md.append("| Decision | Count | Percentage |\n")
    md.append("|----------|-------|------------|\n")
    for decision, count in sorted(results["decisions"].items()):
        pct = count / total * 100
        md.append(f"| {decision.upper()} | {count} | {pct:.1f}% |\n")
    md.append("\n")
    
    md.append("## Rates\n\n")
    md.append(f"- **Hallucination Rate**: {results.get('hallucination_rate', 0):.1%}\n")
    md.append(f"- **Repair Rate**: {results['decisions'].get('repair', 0) / total * 100:.1f}%\n")
    md.append(f"- **Block Rate**: {results['decisions'].get('block', 0) / total * 100:.1f}%\n")
    md.append(f"- **Faithfulness @ threshold**: {results.get('faith_at_threshold', 0):.1%}\n")
    md.append(f"- **Coverage @ threshold**: {results.get('cov_at_threshold', 0):.1%}\n\n")
    
    if policy_presets:
        md.append("## Policy Presets Comparison\n\n")
        md.append("| Preset | Faithfulness | Coverage | Repair Rate | Block Rate | Pass Rate |\n")
        md.append("|--------|--------------|----------|-------------|------------|-----------|\n")
        for preset_name, preset_data in policy_presets.items():
            md.append(f"| {preset_name} | {preset_data.get('faith', 0):.2f} | {preset_data.get('cov', 0):.2f} | "
                     f"{preset_data.get('repair_rate', 0):.1%} | {preset_data.get('block_rate', 0):.1%} | "
                     f"{preset_data.get('pass_rate', 0):.1%} |\n")
        md.append("\n")
    
    # Domain breakdown
    if "by_domain" in results:
        md.append("## Performance by Domain\n\n")
        md.append("| Domain | Total | Passed | Pass Rate |\n")
        md.append("|--------|-------|--------|----------|\n")
        for domain, stats in results["by_domain"].items():
            pass_rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            md.append(f"| {domain} | {stats['total']} | {stats['passed']} | {pass_rate:.1f}% |\n")
        md.append("\n")
    
    return "".join(md)


def main():
    parser = argparse.ArgumentParser(description="Run evaluation harness")
    parser.add_argument("--csv", help="Use CSV benchmark file instead of JSON cases")
    parser.add_argument("--report", choices=["md"], help="Generate markdown report")
    args = parser.parse_args()
    
    if args.csv:
        cases_iter = load_cases_csv(args.csv)
    else:
        folder = os.path.join(os.path.dirname(__file__), "cases")
        if not os.path.isdir(folder) or len(glob.glob(os.path.join(folder, "*.json"))) < 5:
            print("No cases found. Run: python eval/generate_cases.py")
            sys.exit(2)
        cases_iter = load_cases_json(folder)
    
    n = 0
    oks = 0
    faith, cov, tox = [], [], []
    decisions = {"allow": 0, "repair": 0, "block": 0}
    mismatches = []
    by_domain = defaultdict(lambda: {"total": 0, "passed": 0})
    
    from app.policy import load_policy
    policy = load_policy()
    faith_threshold = policy.thresholds.faithfulness_min
    cov_threshold = policy.thresholds.coverage_min
    
    faith_at_threshold = 0
    cov_at_threshold = 0
    
    for name, case in cases_iter:
        exp = case["expect"]
        domain = case.get("name", "").split("_")[0] if "_" in case.get("name", "") else "unknown"
        res = evaluate_payload(case["input"])
        got = res["decision"]
        n += 1
        decisions[got] = decisions.get(got, 0) + 1
        s = res["scores"]
        faith.append(s["faithfulness"])
        cov.append(s["coverage"])
        tox.append(s["toxicity"])
        
        if s["faithfulness"] >= faith_threshold:
            faith_at_threshold += 1
        if s["coverage"] >= cov_threshold:
            cov_at_threshold += 1
        
        by_domain[domain]["total"] += 1
        if got == exp:
            oks += 1
            by_domain[domain]["passed"] += 1
        else:
            mismatches.append((name, exp, got, domain))
    
    results = {
        "total": n,
        "passed": oks,
        "decisions": decisions,
        "faith_avg": statistics.mean(faith) if faith else 0,
        "cov_avg": statistics.mean(cov) if cov else 0,
        "tox_avg": statistics.mean(tox) if tox else 0,
        "faith_at_threshold": faith_at_threshold / n if n > 0 else 0,
        "cov_at_threshold": cov_at_threshold / n if n > 0 else 0,
        "hallucination_rate": (decisions.get("repair", 0) + decisions.get("block", 0)) / n if n > 0 else 0,
        "by_domain": dict(by_domain),
    }
    
    if args.report == "md":
        md_report = generate_markdown_report(results)
        print(md_report)
        report_path = os.path.join(os.path.dirname(__file__), "report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_report)
        print(f"\nReport written to {report_path}")
    else:
        print("\n=== Eval Summary ===")
        print(f"Total: {n}, Passed: {oks}, Failed: {n-oks}")
        print(f"Decisions: {decisions}")
        print(f"Faithfulness avg={statistics.mean(faith):.2f}")
        print(f"Coverage     avg={statistics.mean(cov):.2f}")
        print(f"Toxicity     avg={statistics.mean(tox):.2f}")
        
        if mismatches:
            print("\nMismatches:")
            for m in mismatches[:10]:
                print(" -", m)
    
    # non-zero exit on failure
    sys.exit(0 if oks == n else 3)


if __name__ == "__main__":
    main()
