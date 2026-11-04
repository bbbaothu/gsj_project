"""
Pytest fixtures cho kiểm thử Module Tổng quan kho.
"""
import os
import sqlite3
import pytest

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "retail_dienmay.db"))

@pytest.fixture(scope="session")
def db_path():
    assert os.path.exists(DB_PATH), f"Database file not found at {DB_PATH}"
    return DB_PATH

@pytest.fixture
def db_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
