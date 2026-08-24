import pytest
import os
from app.ml.detection.tfidf_classifier import TFIDFContentClassifier

def test_classifier_prediction():
    classifier = TFIDFContentClassifier()
    human_sample = "Researchers at the observatory documented stellar spectra and published observations in Nature."
    ai_sample = "It is important to remember that as an AI language model, exploring the intricate nuances of sustainable architecture reveals modern solutions."

    p_h1, p_ai1 = classifier.predict_proba(human_sample)
    p_h2, p_ai2 = classifier.predict_proba(ai_sample)

    assert p_h1 + p_ai1 == pytest.approx(1.0, abs=0.01)
    assert p_h2 + p_ai2 == pytest.approx(1.0, abs=0.01)
    assert classifier.predict(human_sample) in ["HUMAN", "AI_GENERATED"]
    assert classifier.predict(ai_sample) in ["HUMAN", "AI_GENERATED"]

def test_classifier_metadata():
    classifier = TFIDFContentClassifier()
    meta = classifier.get_model_metadata()
    assert "version" in meta
    assert "operational_status" in meta
    assert meta["model_type"] == "TFIDF_LOGISTIC_REGRESSION"
