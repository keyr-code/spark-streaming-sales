import pytest
import psycopg2
import os


def test_database_connection():
    """Test database connectivity - skip if no database available"""
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://root:root@localhost:5432/goods_store"
    )

    if not os.getenv("DATABASE_URL"):
        pytest.skip("No database configured for testing")

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        conn.close()
    except psycopg2.OperationalError:
        pytest.skip("Database not available")


def test_database_tables():
    """Test that required tables exist - skip if no database"""
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://root:root@localhost:5432/goods_store"
    )

    if not os.getenv("DATABASE_URL"):
        pytest.skip("No database configured for testing")

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        )

        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Add your expected table names here
        expected_tables = ["products", "orders"]  # Example tables
        for table in expected_tables:
            assert table in tables, f"Table {table} not found"
    except psycopg2.OperationalError:
        pytest.skip("Database not available")
