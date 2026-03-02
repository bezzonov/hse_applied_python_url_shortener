# database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL must be set in .env file or environment variables")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
rdb = redis.from_url(REDIS_URL)

# Импортируем модели в конце
from models import Base
Base.metadata.create_all(bind=engine)
