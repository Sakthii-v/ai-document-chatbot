from app.db.database import engine, Base
import app.models  # Ensure models are imported before creating tables


def init_db():
    Base.metadata.create_all(bind=engine)
