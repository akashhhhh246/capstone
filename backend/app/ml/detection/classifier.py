from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class ContentClassifier(ABC):
    """
    Abstract interface for AI vs Human text content classifiers.
    Allows seamless swapping between TF-IDF baselines, RoBERTa/DeBERTa detectors,
    and foundation model discriminators.
    """

    @abstractmethod
    def predict(self, text: str) -> str:
        """Return predicted class ('HUMAN' or 'AI_GENERATED')."""
        pass

    @abstractmethod
    def predict_proba(self, text: str) -> Tuple[float, float]:
        """
        Return calibrated probabilities: (p_human, p_ai).
        Sum of probabilities equals 1.0.
        """
        pass

    @abstractmethod
    def get_model_metadata(self) -> Dict[str, Any]:
        """Return model name, version, training details, and metrics."""
        pass
