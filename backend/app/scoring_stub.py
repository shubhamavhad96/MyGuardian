import random
from .schemas import Scores


def fake_scores() -> Scores:
    return Scores(
        faithfulness=round(random.uniform(0.6, 0.98), 2),
        coverage=round(random.uniform(0.4, 0.95), 2),
        toxicity=round(random.uniform(0.0, 0.1), 2),
    )


def decide(scores: Scores, f_min: float, c_min: float, tox_max: float):
    if scores.toxicity > tox_max:
        return "block", ["Toxicity too high"]
    if scores.faithfulness < f_min or scores.coverage < c_min:
        return "repair", ["Needs improvement per thresholds"]
    return "allow", []
