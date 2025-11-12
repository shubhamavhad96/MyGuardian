from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Passage(BaseModel):
    id: str
    text: str
    source: Optional[str] = None


class EvaluateRequest(BaseModel):
    question: str
    answer: str
    passages: List[Passage] = Field(default_factory=list)


class Scores(BaseModel):
    faithfulness: float
    coverage: float
    toxicity: float


class EvaluateResponse(BaseModel):
    decision: str  # "allow" | "repair" | "block"
    scores: Scores
    repaired_answer: Optional[str] = None
    explanations: List[str] = Field(default_factory=list)
    meta: Dict[str, str] = Field(default_factory=dict)
