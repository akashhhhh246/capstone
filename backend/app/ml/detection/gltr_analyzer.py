import math
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class GLTRTokenResult:
    token: str
    rank: int
    bucket: str  # 'green' (top 10), 'yellow' (top 100), 'red' (top 1000), 'purple' (tail > 1000)
    prob: float
    log_prob: float

class GLTRStatisticalAnalyzer:
    """
    GLTR-inspired (Giant Language model Test Room) statistical token probability analyzer.
    Analyzes whether tokens in a text disproportionately match high-probability predictions
    from language models (characteristic of greedily or top-k sampled AI generation)
    versus human text which contains more unexpected, creative, or low-probability words.
    
    Provides both statistical token evaluation and clearly designated demonstration/heuristic modes.
    """

    VERSION = "gltr-stat-v1.0"

    # Reference frequency rank dictionary for English word frequencies (Brown + OpenWebText approximation)
    # Allows fast, zero-GPU baseline token rank estimation
    FREQ_RANK_TIERS = {
        # Top 10 words
        "the": 1, "be": 2, "to": 3, "of": 4, "and": 5, "a": 6, "in": 7, "that": 8, "have": 9, "i": 10,
        "it": 11, "for": 12, "not": 13, "on": 14, "with": 15, "he": 16, "as": 17, "you": 18, "do": 19, "at": 20,
    }

    def __init__(self, mode: str = "DEMONSTRATION_STATISTICAL"):
        self.mode = mode  # "ACTUAL_MODEL_BASED" or "DEMONSTRATION_STATISTICAL"

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform token-by-token statistical ranking analysis.
        Returns visual token spans, bucket percentages, estimated perplexity, and AI indicators.
        """
        if not text or not text.strip():
            return {
                "tokens": [],
                "bucket_distribution": {"green": 0.0, "yellow": 0.0, "red": 0.0, "purple": 0.0},
                "estimated_perplexity": 0.0,
                "entropy": 0.0,
                "ai_likelihood_indicator": 0.0,
                "analysis_mode": self.mode,
                "methodology": "Statistical token frequency rank bucket distribution.",
                "disclaimer": "This is a statistical demonstration model estimating token likelihood tiers."
            }

        # Tokenize preserving punctuation/spacing chunks for UI rendering
        raw_tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
        token_results: List[Dict[str, Any]] = []
        
        green_count = 0
        yellow_count = 0
        red_count = 0
        purple_count = 0
        total_eval_tokens = 0
        total_log_prob = 0.0

        for token in raw_tokens:
            # If whitespace, pass through without evaluation
            if token.isspace():
                token_results.append({
                    "token": token,
                    "rank": -1,
                    "bucket": "whitespace",
                    "prob": 1.0,
                    "log_prob": 0.0
                })
                continue

            cleaned_t = token.lower()
            
            # Estimate token rank and probability
            rank, prob, bucket = self._estimate_token_rank(cleaned_t)
            log_prob = math.log(max(1e-7, prob))
            total_log_prob += log_prob
            total_eval_tokens += 1

            if bucket == "green":
                green_count += 1
            elif bucket == "yellow":
                yellow_count += 1
            elif bucket == "red":
                red_count += 1
            else:
                purple_count += 1

            token_results.append({
                "token": token,
                "rank": rank,
                "bucket": bucket,
                "prob": round(prob, 4),
                "log_prob": round(log_prob, 4)
            })

        n = max(1, total_eval_tokens)
        green_pct = round(green_count / n, 4)
        yellow_pct = round(yellow_count / n, 4)
        red_pct = round(red_count / n, 4)
        purple_pct = round(purple_count / n, 4)

        # Perplexity estimation: 2^(-(1/N) * sum(log2(p)))
        cross_entropy = - (total_log_prob / math.log(2)) / n if n > 0 else 0.0
        estimated_ppl = round(math.pow(2, min(15.0, cross_entropy)), 2)

        # AI Likelihood indicator: LLM outputs typically have > 60% green tokens and < 10% purple tokens
        ai_indicator = round(min(1.0, max(0.0, (green_pct * 0.7 + yellow_pct * 0.3) - (purple_pct * 0.5))), 3)

        return {
            "tokens": token_results,
            "bucket_distribution": {
                "green": green_pct,      # Top 10 (High probability)
                "yellow": yellow_pct,    # Top 100 (Medium-high)
                "red": red_pct,          # Top 1000 (Medium-low)
                "purple": purple_pct     # Tail > 1000 (Low probability / Unpredictable)
            },
            "token_counts": {
                "green": green_count,
                "yellow": yellow_count,
                "red": red_count,
                "purple": purple_count,
                "total_evaluated": total_eval_tokens
            },
            "estimated_perplexity": estimated_ppl,
            "mean_cross_entropy": round(cross_entropy, 3),
            "ai_likelihood_indicator": ai_indicator,
            "analysis_mode": self.mode,
            "methodology": "Statistical token probability ranking inspired by GLTR (Gehrmann et al., Harvard/MIT-IBM).",
            "disclaimer": "HEURISTIC/DEMO ANALYSIS: Approximates vocabulary rank distributions for responsive local execution."
        }

    def _estimate_token_rank(self, word: str) -> (int, float, str):
        """
        Estimate vocabulary rank and assign to standard GLTR color tiers:
        - green: rank 1 - 10
        - yellow: rank 11 - 100
        - red: rank 101 - 1000
        - purple: rank > 1000
        """
        if word in self.FREQ_RANK_TIERS:
            rank = self.FREQ_RANK_TIERS[word]
            prob = 1.0 / (rank + 1)
            bucket = "green" if rank <= 10 else "yellow"
            return rank, prob, bucket

        # Heuristic frequency rank based on word length and common morphological patterns
        length = len(word)
        if length <= 3:
            rank = 45
            prob = 0.05
            bucket = "yellow"
        elif length <= 6:
            rank = 350
            prob = 0.008
            bucket = "red"
        elif length <= 9:
            rank = 750
            prob = 0.002
            bucket = "red"
        else:
            rank = 2500
            prob = 0.0003
            bucket = "purple"

        return rank, prob, bucket
