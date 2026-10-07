import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "AI Backend"
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai")
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRE_SECONDS", "604800"))
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

settings = Settings()
