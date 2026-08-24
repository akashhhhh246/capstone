from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import hashlib
import re

class WatermarkDetector(ABC):
    """
    Abstract interface for LLM text watermark detectors.
    Supports soft green-list token distribution tests, cryptographic watermarks,
    and returns explicit status codes.
    """

    @abstractmethod
    def detect_watermark(self, text: str, scheme: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate text for presence of synthetic watermarking signals.
        Returns:
            status: 'DETECTED' | 'NOT_DETECTED' | 'NOT_SUPPORTED' | 'UNAVAILABLE'
            confidence: float (0.0 - 1.0)
            details: Dict with p-value, z-score, green-list proportion, scheme
        """
        pass

class KirchenbauerWatermarkDetector(WatermarkDetector):
    """
    Kirchenbauer et al. (2023) style green-list token watermark detector.
    Tests if consecutive tokens have pseudo-random hashes that disproportionately
    fall into the pseudo-random 'green' partition keyed by previous token hashes.
    """

    SCHEME_NAME = "Kirchenbauer Green-List Watermark"

    def __init__(self, gamma: float = 0.5, z_threshold: float = 4.0):
        self.gamma = gamma          # Expected green-list proportion under null hypothesis (default 0.5)
        self.z_threshold = z_threshold  # Statistical z-score threshold for rejection of null hypothesis

    def detect_watermark(self, text: str, scheme: Optional[str] = None) -> Dict[str, Any]:
        if not text or len(text.strip()) < 50:
            return {
                "status": "UNAVAILABLE",
                "confidence": 0.0,
                "scheme": self.SCHEME_NAME,
                "details": {
                    "reason": "Text length too short for statistically valid watermark evaluation (min 50 chars)."
                }
            }

        # Tokenize words
        words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', text.lower())
        if len(words) < 15:
            return {
                "status": "UNAVAILABLE",
                "confidence": 0.0,
                "scheme": self.SCHEME_NAME,
                "details": {
                    "reason": f"Insufficient tokens ({len(words)} < 15 required for hypothesis testing)."
                }
            }

        green_hits = 0
        total_pairs = len(words) - 1

        for i in range(total_pairs):
            prev_token = words[i]
            curr_token = words[i + 1]
            # Keyed pseudo-random hash test
            hash_input = f"{prev_token}_{curr_token}".encode("utf-8")
            hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
            is_green = (hash_val % 100) < int(self.gamma * 100)
            if is_green:
                green_hits += 1

        observed_proportion = green_hits / max(1, total_pairs)
        # Compute z-score: (observed - expected) / sqrt(expected * (1 - gamma) / N)
        std_err = ((self.gamma * (1.0 - self.gamma)) / max(1, total_pairs)) ** 0.5
        z_score = (observed_proportion - self.gamma) / max(1e-5, std_err)

        if z_score >= self.z_threshold:
            status = "DETECTED"
            confidence = min(0.99, round(0.5 + (z_score / 10.0), 3))
        else:
            status = "NOT_DETECTED"
            confidence = round(max(0.0, 1.0 - (z_score / self.z_threshold)), 3)

        return {
            "status": status,
            "confidence": confidence,
            "scheme": self.SCHEME_NAME,
            "details": {
                "total_token_pairs": total_pairs,
                "green_list_hits": green_hits,
                "observed_green_ratio": round(observed_proportion, 4),
                "expected_ratio": self.gamma,
                "z_score": round(z_score, 2),
                "z_threshold": self.z_threshold,
                "p_value_estimate": round(0.5 * (1.0 - math.erf(z_score / (2 ** 0.5))), 6) if 'math' in globals() else None,
                "limitations": "Watermark detection depends on key agreement and is fragile against adversarial paraphrasing."
            }
        }

import math
