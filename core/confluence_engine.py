from utils.config import CONFIG
from utils.logger import get_logger

log = get_logger("ConfluenceEngine", CONFIG["logging_level"])

class ConfluenceEngine:
    def __init__(self, weights: dict[str, float], threshold: float):
        self.weights = weights
        self.threshold = threshold

    def score(self, signals: list[dict]) -> dict:
        score = 0.0
        contributing = []
        for s in signals:
            w = self.weights.get(s["event"], 0.0)
            score += w
            if w != 0.0:
                contributing.append((s["event"], w))
        result = {"score": score, "contributing": contributing, "pass": score >= self.threshold}
        log.debug(f"Confluence result: {result}")
        return result
