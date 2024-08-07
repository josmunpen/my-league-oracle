
from .db import SessionLocal


# Create a session per request, then close
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()