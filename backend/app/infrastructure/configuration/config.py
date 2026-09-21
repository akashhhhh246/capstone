import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

# Base backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BACKEND_DIR, "provenance_defense.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Information Integrity & AI Defense Workbench"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database (Absolute Path)
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    
    # Model Artifacts
    MODEL_DIR: str = os.path.join(BACKEND_DIR, "models").replace("\\", "/")
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    TFIDF_MODEL_PATH: str = os.path.join(BACKEND_DIR, "models", "tfidf_classifier.joblib").replace("\\", "/")
    GNN_MODEL_PATH: str = os.path.join(BACKEND_DIR, "models", "gnn_propagation_model.pt").replace("\\", "/")
    
    # Data paths
    SAMPLE_DATASET_JSON: str = os.path.join(BACKEND_DIR, "data", "sample_dataset.json").replace("\\", "/")
    SAMPLE_DATASET_CSV: str = os.path.join(BACKEND_DIR, "data", "sample_dataset.csv").replace("\\", "/")

    # =========================================================================
    # Real-Time Public Data Ingestion Settings
    # =========================================================================
    DATA_SOURCES_ENABLED: str = "gdelt,rss"
    
    # GDELT Project Settings (Primary Free/Public Source)
    GDELT_ENABLED: bool = True
    GDELT_POLL_INTERVAL: int = 900  # seconds (15 minutes)
    GDELT_MAX_RESULTS: int = 25
    GDELT_QUERY_KEYWORDS: str = "disinformation OR \"fake news\" OR \"generative AI\" OR LLM OR deepfake OR propaganda OR \"cyberattack\" OR \"influence operation\""
    GDELT_LANGUAGE: str = "English"
    GDELT_API_URL: str = "https://api.gdeltproject.org/api/v2/doc/doc"

    # RSS Feeds Settings (Optional Free/Public Source)
    RSS_ENABLED: bool = True
    RSS_POLL_INTERVAL: int = 1800  # seconds (30 minutes)
    RSS_FEEDS: str = "https://feeds.bbci.co.uk/news/technology/rss.xml,https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"

    # Bluesky Settings (Optional Public Stream Interface)
    BLUESKY_ENABLED: bool = False
    BLUESKY_ENDPOINT: str = "https://public.api.bsky.app"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:9207",
        "http://127.0.0.1:9207",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    # Enterprise Production Settings
    SECURITY_HEADERS_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 120
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
