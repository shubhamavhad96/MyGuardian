# MIT License
# Copyright (c) 2024 MyGuardian Contributors

from typing import Dict, Any, Optional
from langchain_core.runnables import Runnable
import httpx


class GuardrailRunnable(Runnable):
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: str = "demo-key-change-in-production",
        mode: str = "enforce",
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.mode = mode
        self.client = httpx.Client(timeout=10.0)
    
    def invoke(self, input: Dict[str, Any], config: Optional[Any] = None) -> Dict[str, Any]:
        question = input.get("question", "")
        answer = input.get("answer", "")
        passages = input.get("passages", [])
        
        headers = {"X-API-Key": self.api_key}
        if self.mode == "shadow":
            headers["X-Guardrail-Mode"] = "shadow"
        
        response = self.client.post(
            f"{self.api_url}/evaluate",
            json={
                "question": question,
                "answer": answer,
                "passages": passages,
            },
            headers=headers,
        )
        response.raise_for_status()
        result = response.json()
        
        if result["decision"] == "block":
            return {
                "decision": "block",
                "answer": "I cannot provide that information due to safety concerns.",
                "scores": result["scores"],
                "explanations": result["explanations"],
            }
        elif result["decision"] == "repair" and result.get("repaired_answer"):
            return {
                "decision": "repair",
                "answer": result["repaired_answer"],
                "scores": result["scores"],
                "explanations": result["explanations"],
            }
        else:
            return {
                "decision": "allow",
                "answer": answer,
                "scores": result["scores"],
                "explanations": result["explanations"],
            }
    
    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()


if __name__ == "__main__":
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    prompt = ChatPromptTemplate.from_template("Answer: {question}")
    chain = prompt | llm
    
    guardrail = GuardrailRunnable()
    
    question = "What are side-effects of metformin?"
    passages = [{"id": "p1", "text": "Common side-effects are nausea and diarrhea.", "source": "med-guide"}]
    
    llm_response = chain.invoke({"question": question})
    answer = llm_response.content if hasattr(llm_response, "content") else str(llm_response)
    
    result = guardrail.invoke({
        "question": question,
        "answer": answer,
        "passages": passages,
    })
    
    print(f"Decision: {result['decision']}")
    print(f"Answer: {result['answer']}")

