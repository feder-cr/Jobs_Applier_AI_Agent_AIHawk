"""SQLite-backed application history tracker."""
from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.logging import logger

DB_PATH = Path("data_folder/applications.db")

# Thread-local storage so each thread gets its own connection
_local = threading.local()


def _get_conn(db_path: Path | None = None) -> sqlite3.Connection:
    path = str(db_path or DB_PATH)
    if not hasattr(_local, "conns"):
        _local.conns = {}
    conn = _local.conns.get(path)
    if conn is not None:
        try:
            conn.execute("SELECT 1")
            return conn
        except sqlite3.ProgrammingError:
            pass
    conn = sqlite3.connect(path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")
    conn.row_factory = sqlite3.Row
    _local.conns[path] = conn
    return conn


class ApplicationTracker:
    """Track job applications in a local SQLite database.

    Each discovered/applied job gets one row. The tracker prevents
    duplicate applications and maintains a full history for the UI.
    """

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = _get_conn(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                platform      TEXT NOT NULL,
                company       TEXT,
                title         TEXT,
                url           TEXT UNIQUE,
                status        TEXT DEFAULT 'pending',
                score         INTEGER,
                score_reason  TEXT,
                applied_at    TEXT,
                discovered_at TEXT NOT NULL,
                resume_path   TEXT,
                cover_path    TEXT,
                notes         TEXT,
                session_id    TEXT
            )
        """)
        conn.commit()
        logger.debug("ApplicationTracker DB initialized at {}", self.db_path)

    def record_discovered(
        self,
        platform: str,
        company: str,
        title: str,
        url: str,
        session_id: str = "",
    ) -> int | None:
        """Insert a newly discovered job. Returns row id, or None if duplicate."""
        now = datetime.now(timezone.utc).isoformat()
        conn = _get_conn(self.db_path)
        try:
            cur = conn.execute(
                """INSERT INTO applications
                   (platform, company, title, url, status, discovered_at, session_id)
                   VALUES (?, ?, ?, ?, 'discovered', ?, ?)""",
                (platform, company, title, url, now, session_id),
            )
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None  # already in DB

    def update_score(self, url: str, score: int, reason: str = "") -> None:
        conn = _get_conn(self.db_path)
        conn.execute(
            "UPDATE applications SET score=?, score_reason=?, status='scored' WHERE url=?",
            (score, reason, url),
        )
        conn.commit()

    def mark_skipped(self, url: str, reason: str = "") -> None:
        conn = _get_conn(self.db_path)
        conn.execute(
            "UPDATE applications SET status='skipped', notes=? WHERE url=?",
            (reason, url),
        )
        conn.commit()

    def mark_applied(self, url: str, resume_path: str = "", cover_path: str = "") -> None:
        now = datetime.now(timezone.utc).isoformat()
        conn = _get_conn(self.db_path)
        conn.execute(
            """UPDATE applications
               SET status='applied', applied_at=?, resume_path=?, cover_path=?
               WHERE url=?""",
            (now, resume_path, cover_path, url),
        )
        conn.commit()

    def mark_failed(self, url: str, reason: str = "") -> None:
        conn = _get_conn(self.db_path)
        conn.execute(
            "UPDATE applications SET status='failed', notes=? WHERE url=?",
            (reason, url),
        )
        conn.commit()

    def already_applied(self, company: str, title: str) -> bool:
        """True if we already applied to this company+title combo."""
        conn = _get_conn(self.db_path)
        row = conn.execute(
            """SELECT 1 FROM applications
               WHERE company=? AND title=? AND status='applied'
               LIMIT 1""",
            (company, title),
        ).fetchone()
        return row is not None

    def url_seen(self, url: str) -> bool:
        """True if this URL is already in the database (any status)."""
        conn = _get_conn(self.db_path)
        row = conn.execute(
            "SELECT 1 FROM applications WHERE url=? LIMIT 1", (url,)
        ).fetchone()
        return row is not None

    def get_applications(
        self,
        platform: str | None = None,
        status: str | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return applications filtered by platform / status."""
        conn = _get_conn(self.db_path)
        conditions = []
        params: list = []
        if platform:
            conditions.append("platform=?")
            params.append(platform)
        if status:
            conditions.append("status=?")
            params.append(status)
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        rows = conn.execute(
            f"SELECT * FROM applications {where} ORDER BY discovered_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()
        return [dict(row) for row in rows]

    def get_application(self, app_id: int) -> dict[str, Any] | None:
        conn = _get_conn(self.db_path)
        row = conn.execute(
            "SELECT * FROM applications WHERE id=?", (app_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_stats(self) -> dict[str, Any]:
        conn = _get_conn(self.db_path)
        total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        applied = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE status='applied'"
        ).fetchone()[0]
        skipped = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE status='skipped'"
        ).fetchone()[0]
        failed = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE status='failed'"
        ).fetchone()[0]
        by_platform = conn.execute(
            "SELECT platform, COUNT(*) FROM applications GROUP BY platform"
        ).fetchall()
        return {
            "total": total,
            "applied": applied,
            "skipped": skipped,
            "failed": failed,
            "by_platform": {row[0]: row[1] for row in by_platform},
        }

    def export_csv(self) -> str:
        """Return all applications as a CSV string."""
        import csv
        import io

        conn = _get_conn(self.db_path)
        rows = conn.execute("SELECT * FROM applications ORDER BY discovered_at DESC").fetchall()
        if not rows:
            return "id,platform,company,title,url,status,score,applied_at\n"
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))
        return output.getvalue()
