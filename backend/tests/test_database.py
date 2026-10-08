"""Tests for SQLite database operations and historical querying."""

import pytest
from backend.app.database.db import get_db_connection, init_db
from backend.app.database.repository import AquacultureRepository
from backend.app.services.recommendation_service import get_recommendation


def test_db_init_and_tables():
    init_db()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r["name"] for r in cur.fetchall()]
        assert "ponds" in tables
        assert "fish_stocks" in tables
        assert "water_measurements" in tables
        assert "feeding_logs" in tables
        assert "recommendations" in tables


def test_repository_save_and_history(normal_pond_input):
    repo = AquacultureRepository()
    rec = get_recommendation(normal_pond_input, persist=False)

    rec_id = repo.save_recommendation(normal_pond_input, rec)
    assert rec_id > 0

    history = repo.get_pond_history(normal_pond_input.pond_id, limit=5)
    assert len(history) > 0
    latest = history[0]
    assert latest["pond_id"] == normal_pond_input.pond_id
    assert "optimized_feed_kg" in latest
    assert "waste_risk_score" in latest
    assert "pollution_risk_score" in latest
    assert "meal_schedule" in latest
