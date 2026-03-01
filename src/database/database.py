import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./insightx_db.db")

# SQLite-specific configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables"""
    Base.metadata.create_all(bind=engine)


def get_sqlite_db_path() -> Path | None:
    """Return SQLite database file path when DATABASE_URL uses sqlite."""
    if not DATABASE_URL.startswith("sqlite:///"):
        return None
    raw_path = DATABASE_URL[len("sqlite:///"):]
    return Path(raw_path)


def check_sqlite_db_health() -> tuple[bool, str]:
    """Validate SQLite database readability for query operations."""
    db_path = get_sqlite_db_path()
    if db_path is None:
        return True, "non-sqlite"

    if not db_path.exists():
        return False, f"missing:{db_path}"

    try:
        if db_path.stat().st_size < 100:
            return False, f"too-small:{db_path}"

        with db_path.open("rb") as f:
            header = f.read(16)
        if header != b"SQLite format 3\x00":
            return False, f"bad-header:{db_path}"

        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("PRAGMA schema_version;").fetchone()
            conn.execute("SELECT name FROM sqlite_master LIMIT 1;").fetchone()
        finally:
            conn.close()

        return True, "ok"
    except Exception as e:
        return False, f"probe-failed:{e}"


def recover_sqlite_db(seed_csv_path: str = "data/upi_transactions_2024.csv") -> tuple[bool, str]:
    """Rebuild SQLite DB file and seed data when DB is invalid."""
    db_path = get_sqlite_db_path()
    if db_path is None:
        return False, "recovery-not-applicable-non-sqlite"

    try:
        engine.dispose()
    except Exception:
        pass

    try:
        db_path.unlink(missing_ok=True)
    except Exception as e:
        return False, f"delete-failed:{e}"

    try:
        init_db()
        from src.database.data_loader import DataLoader

        loader = DataLoader()
        if os.path.exists(seed_csv_path):
            loader.load_and_populate(csv_path=seed_csv_path)
        else:
            loader.load_and_populate(num_synthetic=250000)

        healthy, reason = check_sqlite_db_health()
        return healthy, f"recovered:{reason}"
    except Exception as e:
        return False, f"recovery-failed:{e}"


def get_transaction_count() -> int:
    """Return total transaction count, or 0 if unavailable."""
    try:
        from src.database.models import Transaction
        db = SessionLocal()
        try:
            return db.query(Transaction).count()
        finally:
            db.close()
    except Exception:
        return 0


def seed_data_if_empty(seed_csv_path: str = "data/upi_transactions_2024.csv") -> tuple[bool, int, str]:
    """Seed data if DB is empty. Returns (seeded, row_count, message)."""
    try:
        current_count = get_transaction_count()
        if current_count > 0:
            return False, current_count, "already-seeded"

        from src.database.data_loader import DataLoader

        loader = DataLoader()
        if os.path.exists(seed_csv_path):
            loader.load_and_populate(csv_path=seed_csv_path)
        else:
            loader.load_and_populate(num_synthetic=250000)

        final_count = get_transaction_count()
        return True, final_count, "seeded"
    except Exception as e:
        return False, 0, f"seed-failed:{e}"
