import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Hermes Engineering Crew")
    
    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "gemma3:1b"
    )

    OLLAMA_TIMEOUT = int(
        os.getenv("OLLAMA_TIMEOUT", 300)
    )

    MAX_REPO_FILES = int(
        os.getenv("MAX_REPO_FILES", 8)
    )

    MAX_FILE_CONTENT_LENGTH = int(
        os.getenv(
            "MAX_FILE_CONTENT_LENGTH",
            800
        )
    )


settings = Settings()