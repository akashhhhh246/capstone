import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.ml.detection.preprocessing import TextPreprocessor
from app.ml.detection.tfidf_classifier import TFIDFContentClassifier
from app.ml.detection.gltr_analyzer import GLTRStatisticalAnalyzer
from app.ml.detection.watermark_detector import KirchenbauerWatermarkDetector
from app.domain.entities.models import Content, DetectionResult
from app.application.dto.schemas import DetectionResultResponse, ClassifierResult, GLTRResult, WatermarkResult

from app.infrastructure.configuration.config import settings

class DetectionService:
    """
    Combined Detection Service.
    Coordinates the entire Part 1 ML detection pipeline:
    - Text preprocessing & feature extraction
    - TF-IDF + Logistic Regression classification
    - GLTR-style statistical token probability ranking
    - Kirchenbauer / Cryptographic watermark verification
    - Aggregate indicator synthesis and optional DB persistence.
    """

    def __init__(self, model_path: Optional[str] = None):
        default_model_path = settings.TFIDF_MODEL_PATH
        self.classifier = TFIDFContentClassifier(model_path=model_path or default_model_path)
        self.gltr_analyzer = GLTRStatisticalAnalyzer()
        self.watermark_detector = KirchenbauerWatermarkDetector()

    def analyze_text(
        self,
        text: str,
        domain: str = "general",
        db: Optional[Session] = None,
        register_content: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze submitted text and produce a unified DetectionResult.
        """
        clean = TextPreprocessor.clean_text(text)
        features = TextPreprocessor.extract_features(clean)
        
        # 1. Classifier evaluation
        p_human, p_ai = self.classifier.predict_proba(clean)
        pred_class = "AI_GENERATED" if p_ai > 0.55 else "HUMAN"
        confidence = round(max(p_human, p_ai), 4)
        clf_meta = self.classifier.get_model_metadata()

        # 2. GLTR evaluation
        gltr_res = self.gltr_analyzer.analyze_text(clean)

        # 3. Watermark evaluation
        wm_res = self.watermark_detector.detect_watermark(clean)

        # 4. Synthesize diagnostic indicators
        indicators = []
        if p_ai >= 0.75:
            indicators.append(f"High TF-IDF n-gram correlation with synthetic corpora ({int(p_ai * 100)}%).")
        elif p_ai >= 0.50:
            indicators.append(f"Moderate synthetic stylistic markers ({int(p_ai * 100)}%).")
        else:
            indicators.append(f"Strong lexical variance consistent with human writing ({int(p_human * 100)}%).")

        green_pct = gltr_res["bucket_distribution"]["green"]
        if green_pct > 0.65:
            indicators.append(f"Elevated top-10 predictable token ratio ({int(green_pct * 100)}%), typical of greedy LLM sampling.")
        if features["burstiness"] < 0.25:
            indicators.append("Low sentence-length burstiness variance (uniform cadence).")
        if wm_res["status"] == "DETECTED":
            indicators.append("Statistically significant green-list token watermark pattern detected.")

        now_iso = datetime.now(timezone.utc).isoformat()
        
        content_id = None
        # Optional persistence
        if register_content and db is not None:
            text_hash = hashlib.sha256(clean.encode("utf-8")).hexdigest()
            # Check existing content
            existing = db.query(Content).filter(Content.text_hash == text_hash).first()
            if existing:
                content_id = existing.id
            else:
                new_content = Content(
                    text_hash=text_hash,
                    raw_text=text,
                    clean_text=clean,
                    source_label="analyst_submission",
                    domain=domain,
                    word_count=features["word_count"],
                    char_count=features["char_count"]
                )
                db.add(new_content)
                db.flush()
                content_id = new_content.id

            # Save DetectionResult
            det_record = DetectionResult(
                content_id=content_id,
                classification=pred_class,
                confidence=confidence,
                ai_probability=p_ai,
                model_version=self.classifier.VERSION,
                gltr_stats=gltr_res["bucket_distribution"],
                watermark_status=wm_res["status"],
                watermark_details=wm_res["details"],
                statistical_features=features,
                indicators=indicators,
                is_heuristic_fallback=not self.classifier.is_trained
            )
            db.add(det_record)
            db.commit()

        return {
            "content_id": content_id,
            "classification": pred_class,
            "confidence": confidence,
            "ai_probability": p_ai,
            "classifier_result": {
                "predicted_class": pred_class,
                "p_human": p_human,
                "p_ai": p_ai,
                "confidence": confidence,
                "model_version": self.classifier.VERSION,
                "is_trained": self.classifier.is_trained
            },
            "gltr_result": gltr_res,
            "watermark_result": wm_res,
            "statistical_features": features,
            "indicators": indicators,
            "model_version": self.classifier.VERSION,
            "timestamp": now_iso,
            "disclaimer": "AI-generated probability is a statistical estimate and not definitive proof of origin or intent. Human analyst review is required."
        }
