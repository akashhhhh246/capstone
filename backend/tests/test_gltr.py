import pytest
from app.ml.detection.gltr_analyzer import GLTRStatisticalAnalyzer
from app.ml.detection.watermark_detector import KirchenbauerWatermarkDetector

def test_gltr_analysis():
    analyzer = GLTRStatisticalAnalyzer()
    text = "The quick brown fox jumps over the lazy dog and runs through the forest."
    result = analyzer.analyze_text(text)

    assert "bucket_distribution" in result
    assert "green" in result["bucket_distribution"]
    assert "yellow" in result["bucket_distribution"]
    assert "red" in result["bucket_distribution"]
    assert "purple" in result["bucket_distribution"]
    assert len(result["tokens"]) > 0
    assert result["analysis_mode"] == "DEMONSTRATION_STATISTICAL"
    assert "disclaimer" in result

def test_watermark_detector():
    detector = KirchenbauerWatermarkDetector()
    short_text = "Hello world"
    res_short = detector.detect_watermark(short_text)
    assert res_short["status"] == "UNAVAILABLE"

    longer_text = "This is a longer scientific paragraph discussing the implementation details of machine learning classifiers and neural network architectures for detecting AI-generated disinformation across digital communication platforms."
    res_long = detector.detect_watermark(longer_text)
    assert res_long["status"] in ["DETECTED", "NOT_DETECTED", "NOT_SUPPORTED", "UNAVAILABLE"]
    assert "details" in res_long
