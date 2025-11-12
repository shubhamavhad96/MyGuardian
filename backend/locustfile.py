from locust import HttpUser, task, between

PAYLOAD = {
    "question": "What are side-effects of metformin and rare risks?",
    "answer": "Common side-effects include nausea and diarrhea. Rarely, lactic acidosis may occur.",
    "passages": [
        {"id": "p1", "text": "Common side-effects are nausea and diarrhea.",
            "source": "med-guide"},
        {"id": "p2", "text": "Rare adverse events include lactic acidosis.",
            "source": "safety-note"}
    ]
}


class GuardrailUser(HttpUser):
    wait_time = between(0.05, 0.2)

    @task
    def evaluate(self):
        self.client.post("/evaluate", json=PAYLOAD)
