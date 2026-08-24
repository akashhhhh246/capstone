import pytest
from app.ml.detection.preprocessing import TextPreprocessor

def test_clean_text():
    raw = "  This   is a \n\n test with   extra   spaces.  "
    clean = TextPreprocessor.clean_text(raw)
    assert clean == "This is a test with extra spaces."

def test_tokenize_words():
    text = "The quick brown fox jumps over the lazy dog!"
    tokens = TextPreprocessor.tokenize_words(text)
    assert len(tokens) == 9
    assert tokens[0] == "the"

def test_split_sentences():
    text = "First sentence here. Second sentence starts now! Is this the third?"
    sentences = TextPreprocessor.split_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "First sentence here."

def test_entropy_and_burstiness():
    text = "This is a simple text. It has short sentences. Sometimes sentences are very long and contain complex explanatory thoughts that demonstrate human writing variance."
    features = TextPreprocessor.extract_features(text)
    assert features["word_count"] > 10
    assert features["shannon_entropy"] > 0.0
    assert features["lexical_diversity_ttr"] > 0.0
    assert "burstiness" in features
