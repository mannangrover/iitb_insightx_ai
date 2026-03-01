from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from src.database.database import init_db, DATABASE_URL
from src.api.routes import router
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="InsightX - Conversational AI for Payment Analytics",
    description="Natural language interface for querying transaction data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
def _get_sqlite_db_path(database_url: str) -> Path | None:
    if not database_url.startswith("sqlite:///"):
        return None
    raw_path = database_url[len("sqlite:///"):]
    return Path(raw_path)


def _is_valid_sqlite_file(db_path: Path) -> bool:
    if not db_path.exists() or db_path.stat().st_size < 100:
        return False
    try:
        with db_path.open("rb") as f:
            header = f.read(16)
        return header == b"SQLite format 3\x00"
    except Exception:
        return False


@app.on_event("startup")
async def startup_event():
    """Initialize database and load data if needed, recovering from invalid DB files."""
    try:
        sqlite_path = _get_sqlite_db_path(DATABASE_URL)

        # Recover from invalid/corrupt SQLite files (e.g., accidental text/LFS pointer file)
        if sqlite_path and sqlite_path.exists() and not _is_valid_sqlite_file(sqlite_path):
            print(f"⚠ Invalid SQLite file detected at {sqlite_path}. Recreating database...")
            sqlite_path.unlink(missing_ok=True)

        init_db()
        print("✓ Database initialized successfully")
        
        # Check if database has data, if not load sample data
        from src.database.database import SessionLocal
        from src.database.models import Transaction
        
        db = SessionLocal()
        try:
            transaction_count = db.query(Transaction).count()
        except Exception as db_error:
            db.close()
            print(f"⚠ Database check failed: {db_error}")
            if sqlite_path and sqlite_path.exists():
                print("⚠ Rebuilding SQLite database from scratch...")
                sqlite_path.unlink(missing_ok=True)
            init_db()
            db = SessionLocal()
            transaction_count = db.query(Transaction).count()
        finally:
            db.close()
        
        if transaction_count == 0:
            print("📦 Database is empty. Loading sample transactions...")
            from src.database.data_loader import DataLoader
            loader = DataLoader()
            seed_csv = os.getenv("SEED_CSV_PATH", "data/upi_transactions_2024.csv")
            if os.path.exists(seed_csv):
                loader.load_and_populate(csv_path=seed_csv)
            else:
                loader.load_and_populate(num_synthetic=250000)
            print("✓ Sample data loaded successfully")
    except Exception as e:
        print(f"✗ Startup error: {e}")
        # Don't crash, continue with empty database if needed

# Include routes
app.include_router(router, prefix="/api", tags=["queries"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "InsightX Conversational AI",
        "description": "Natural language interface for digital payment analytics",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query (POST)",
            "health": "/api/health (GET)",
            "supported_entities": "/api/supported-entities (GET)",
            "example_queries": "/api/example-queries (GET)"
        },
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # Railway sets PORT env var, fallback to 8000 for local
    port = int(os.getenv("PORT", os.getenv("FASTAPI_PORT", 8000)))
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    
    print(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False
    )
