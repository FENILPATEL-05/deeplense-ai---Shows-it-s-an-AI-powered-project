import logging
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor

from config import settings

logger = logging.getLogger(__name__)

_conn = None


def _get_connection():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(settings.POSTGRES_URL)
        _conn.autocommit = True
        logger.info("Connected to PostgreSQL")
    else:
        # Verify connection is still alive, reconnect if needed
        try:
            with _conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (psycopg2.OperationalError, psycopg2.DatabaseError):
            logger.info("PostgreSQL connection lost, reconnecting...")
            _conn = psycopg2.connect(settings.POSTGRES_URL)
            _conn.autocommit = True
    return _conn


def init_db():
    conn = _get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                filename TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL,
                category TEXT,
                tags TEXT[] DEFAULT '{}',
                uploaded_at TIMESTAMP DEFAULT NOW()
            )
        """)
    logger.info("Database initialized — images table ready")


def insert_image(filename: str, path: str, category: str | None = None, tags: list[str] | None = None):
    conn = _get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO images (filename, path, category, tags)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (filename) DO NOTHING
            """,
            (filename, path, category, tags or []),
        )
    logger.info("Inserted image record: %s", filename)


def get_filters() -> dict:
    conn = _get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT DISTINCT category FROM images WHERE category IS NOT NULL ORDER BY category")
        categories = [row["category"] for row in cur.fetchall()]

        cur.execute("SELECT DISTINCT unnest(tags) AS tag FROM images ORDER BY tag")
        tags = [row["tag"] for row in cur.fetchall()]

    return {"categories": categories, "tags": tags}


def filename_exists(filename: str) -> bool:
    conn = _get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM images WHERE filename = %s LIMIT 1", (filename,))
        return cur.fetchone() is not None


def get_all_images(limit: int = 200, offset: int = 0) -> list[dict]:
    conn = _get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT filename, path, category, tags, uploaded_at FROM images ORDER BY uploaded_at DESC LIMIT %s OFFSET %s",
            (limit, offset),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def count_images() -> int:
    conn = _get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM images")
        return cur.fetchone()[0]
