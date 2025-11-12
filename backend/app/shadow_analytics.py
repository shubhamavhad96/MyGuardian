import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


class ShadowTracker:
    def __init__(self):
        self.decisions: List[Dict] = []
        self.max_size = 10000
    
    def record(self, question: str, answer: str, shadow_decision: str, scores: Dict, 
               question_len: int = None, answer_len: int = None):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "question": question[:200],
            "answer": answer[:200],
            "question_len": question_len or len(question),
            "answer_len": answer_len or len(answer),
            "shadow_decision": shadow_decision,
            "scores": scores,
        }
        self.decisions.append(entry)
        if len(self.decisions) > self.max_size:
            self.decisions = self.decisions[-self.max_size:]
    
    def get_disagreements(self, enforce_decision: str) -> List[Dict]:
        return [d for d in self.decisions if d["shadow_decision"] != enforce_decision]
    
    def generate_daily_report(self) -> Dict:
        today = datetime.utcnow().date().isoformat()
        today_decisions = [
            d for d in self.decisions 
            if d["timestamp"].startswith(today)
        ]
        
        if not today_decisions:
            return {"date": today, "total": 0, "message": "No shadow decisions today"}
        
        decisions_by_type = defaultdict(int)
        for d in today_decisions:
            decisions_by_type[d["shadow_decision"]] += 1
        
        top_blocked = sorted(
            [d for d in today_decisions if d["shadow_decision"] == "block"],
            key=lambda x: x["scores"].get("toxicity", 0),
            reverse=True
        )[:10]
        
        top_repaired = sorted(
            [d for d in today_decisions if d["shadow_decision"] == "repair"],
            key=lambda x: (
                max(0, 0.15 - x["scores"].get("faithfulness", 0)) +
                max(0, 0.60 - x["scores"].get("coverage", 0))
            ),
            reverse=True
        )[:10]
        
        report = {
            "date": today,
            "total": len(today_decisions),
            "decisions": dict(decisions_by_type),
            "top_blocked": [
                {
                    "question": d["question"],
                    "toxicity": d["scores"].get("toxicity", 0),
                    "reason": "High toxicity/PII detected"
                }
                for d in top_blocked
            ],
            "top_repaired": [
                {
                    "question": d["question"],
                    "faithfulness": d["scores"].get("faithfulness", 0),
                    "coverage": d["scores"].get("coverage", 0),
                    "reason": f"Low faithfulness ({d['scores'].get('faithfulness', 0):.2f}) or coverage ({d['scores'].get('coverage', 0):.2f})"
                }
                for d in top_repaired
            ],
        }
        
        report_path = REPORTS_DIR / f"shadow-{today}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report


_shadow_tracker = ShadowTracker()


def get_shadow_tracker() -> ShadowTracker:
    return _shadow_tracker

