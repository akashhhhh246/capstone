import re
import math
import collections
from typing import Dict, Any, List

class TextPreprocessor:
    """
    Modular text preprocessing and statistical feature extraction engine.
    Extracts stylometric and complexity features relevant to AI vs human text detection.
    """
    
    # Common English stopwords
    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
        "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
        "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
        "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
        "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
        "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
        "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
        "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
        "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
        "they've", "this", "those", "through", "to", "too", "under", "until", "up",
        "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
        "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
        "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
        "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
        "yourself", "yourselves"
    }

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Normalize whitespaces, strip zero-width characters, and trim."""
        if not text:
            return ""
        # Remove zero-width spaces and control chars
        cleaned = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    @classmethod
    def tokenize_words(cls, text: str, lowercase: bool = True) -> List[str]:
        """Extract alphanumeric words."""
        cleaned = cls.clean_text(text)
        if lowercase:
            cleaned = cleaned.lower()
        return re.findall(r'\b[a-zA-Z0-9_\'-]+\b', cleaned)

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        """Split text into sentences using regex boundary detection."""
        cleaned = cls.clean_text(text)
        if not cleaned:
            return []
        sentences = re.split(r'(?<=[.!?])\s+', cleaned)
        return [s.strip() for s in sentences if s.strip()]

    @classmethod
    def calculate_shannon_entropy(cls, text: str) -> float:
        """Calculate Shannon entropy over character distribution."""
        if not text:
            return 0.0
        counts = collections.Counter(text)
        total_len = len(text)
        entropy = 0.0
        for count in counts.values():
            prob = count / total_len
            if prob > 0:
                entropy -= prob * math.log2(prob)
        return round(entropy, 4)

    @classmethod
    def calculate_burstiness(cls, sentences: List[str]) -> float:
        """
        Calculate sentence length variance / burstiness.
        LLMs typically exhibit more uniform sentence lengths (lower burstiness)
        compared to human writing which varies widely.
        """
        if len(sentences) < 2:
            return 0.0
        lengths = [len(cls.tokenize_words(s)) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        if mean_len == 0:
            return 0.0
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        # Coefficient of variation (burstiness metric)
        return round(std_dev / mean_len, 4)

    @classmethod
    def extract_features(cls, text: str) -> Dict[str, Any]:
        """Extract comprehensive statistical and stylometric features."""
        clean = cls.clean_text(text)
        words = cls.tokenize_words(clean)
        sentences = cls.split_sentences(clean)
        
        char_count = len(clean)
        word_count = len(words)
        sentence_count = max(1, len(sentences))
        
        avg_word_length = round(sum(len(w) for w in words) / max(1, word_count), 2)
        avg_sentence_length = round(word_count / sentence_count, 2)
        
        # Type-Token Ratio (Lexical Diversity)
        unique_words = set(w.lower() for w in words)
        ttr = round(len(unique_words) / max(1, word_count), 4)
        
        # Stopword ratio
        stopword_count = sum(1 for w in words if w.lower() in cls.STOPWORDS)
        stopword_ratio = round(stopword_count / max(1, word_count), 4)
        
        # Uppercase ratio
        upper_chars = sum(1 for c in clean if c.isupper())
        uppercase_ratio = round(upper_chars / max(1, char_count), 4)
        
        # Punctuation ratio
        punct_chars = sum(1 for c in clean if c in '.,!?;:"()[]{}-—')
        punctuation_ratio = round(punct_chars / max(1, char_count), 4)
        
        # Entropy & burstiness
        entropy = cls.calculate_shannon_entropy(clean)
        burstiness = cls.calculate_burstiness(sentences)
        
        return {
            "char_count": char_count,
            "word_count": word_count,
            "sentence_count": len(sentences),
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
            "lexical_diversity_ttr": ttr,
            "stopword_ratio": stopword_ratio,
            "uppercase_ratio": uppercase_ratio,
            "punctuation_ratio": punctuation_ratio,
            "shannon_entropy": entropy,
            "burstiness": burstiness,
        }
