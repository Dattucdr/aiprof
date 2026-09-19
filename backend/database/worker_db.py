from database.database import SessionLocal


def get_worker_db():
    db = SessionLocal()

    try:
        return db

    except Exception:
        db.close()
        raise
