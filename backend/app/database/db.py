"""SQLite database connection and schema management for AquaNex AI."""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from backend.app.config.settings import settings

logger = logging.getLogger("Database")


def get_db_path() -> Path:
    """Return SQLite database file path."""
    return settings.db_path


@contextmanager
def get_db_connection():
    """Context manager providing a parameterized SQLite connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error("Database transaction rolled back due to: %s", exc)
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database schema tables and indexes."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Ponds table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ponds (
                pond_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                volume_m3 REAL NOT NULL DEFAULT 500.0,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Fish stock information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fish_stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pond_id TEXT NOT NULL,
                species TEXT NOT NULL,
                growth_stage TEXT NOT NULL,
                fish_age_days INTEGER NOT NULL,
                fish_count INTEGER NOT NULL,
                biomass_kg REAL NOT NULL,
                average_fish_weight_g REAL NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pond_id) REFERENCES ponds(pond_id) ON DELETE CASCADE
            );
        """)

        # 3. Water measurements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pond_id TEXT NOT NULL,
                water_temperature_c REAL NOT NULL,
                dissolved_oxygen_mg_l REAL NOT NULL,
                ph REAL NOT NULL,
                ammonia_mg_l REAL NOT NULL,
                nitrate_mg_l REAL NOT NULL,
                turbidity REAL NOT NULL,
                salinity_ppt REAL NOT NULL DEFAULT 0.0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pond_id) REFERENCES ponds(pond_id) ON DELETE CASCADE
            );
        """)

        # 4. Feeding history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feeding_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pond_id TEXT NOT NULL,
                feed_quantity_kg REAL NOT NULL,
                meal_count INTEGER NOT NULL DEFAULT 2,
                feed_quality_score REAL NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pond_id) REFERENCES ponds(pond_id) ON DELETE CASCADE
            );
        """)

        # 5. Recommendations & predictions history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pond_id TEXT NOT NULL,
                recommended_feed_kg REAL NOT NULL,
                optimized_feed_kg REAL NOT NULL,
                expected_waste_kg REAL NOT NULL,
                waste_risk_score INTEGER NOT NULL,
                waste_risk_level TEXT NOT NULL,
                pollution_risk_score INTEGER NOT NULL,
                pollution_risk_level TEXT NOT NULL,
                number_of_meals INTEGER NOT NULL,
                meal_schedule_json TEXT NOT NULL,
                explanation_summary TEXT NOT NULL,
                baseline_feed_kg REAL,
                cost_saved_usd REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pond_id) REFERENCES ponds(pond_id) ON DELETE CASCADE
            );
        """)

        # Indexes for fast historical queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_pond ON fish_stocks(pond_id, recorded_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_water_pond ON water_measurements(pond_id, recorded_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feed_pond ON feeding_logs(pond_id, recorded_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rec_pond ON recommendations(pond_id, recorded_at);")

        logger.info("Database schema verified and tables created.")
