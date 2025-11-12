import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    FAITHFULNESS_MIN = float(os.getenv("FAITHFULNESS_MIN", "0.85"))
    COVERAGE_MIN = float(os.getenv("COVERAGE_MIN", "0.70"))
    TOXICITY_MAX = float(os.getenv("TOXICITY_MAX", "0.05"))
    EVAL_TIMEOUT_SEC = int(os.getenv("EVAL_TIMEOUT_SEC", "5"))


settings = Settings()
