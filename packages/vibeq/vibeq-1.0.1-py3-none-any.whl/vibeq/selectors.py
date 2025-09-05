"""Selector store and simple healing engine for VibeQ

This module provides a small SQLite-backed selector store and basic healing
mechanisms: try stored selectors, record successes/failures, and log healed
events. It's intentionally small and synchronous for MVP use.
"""

import os
import sqlite3
import threading
import time
from typing import List, Dict, Optional

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")
DB_FILE = os.path.join(DB_DIR, "selectors.sqlite")


class SelectorStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_FILE
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._ensure_tables()

    def _ensure_tables(self):
        with self._lock:
            c = self._conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS selectors (
                    id INTEGER PRIMARY KEY,
                    element_key TEXT,
                    selector TEXT,
                    type TEXT,
                    confidence REAL,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_seen REAL
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS healed_events (
                    id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    step TEXT,
                    element_key TEXT,
                    old_selector TEXT,
                    new_selector TEXT
                )
                """
            )
            self._conn.commit()

    def add_selector(self, element_key: str, selector: str, sel_type: str = "css", confidence: float = 0.5):
        with self._lock:
            c = self._conn.cursor()
            c.execute(
                "SELECT id FROM selectors WHERE element_key=? AND selector=?",
                (element_key, selector),
            )
            row = c.fetchone()
            if row:
                return row[0]
            now = time.time()
            c.execute(
                "INSERT INTO selectors (element_key, selector, type, confidence, last_seen) VALUES (?,?,?,?,?)",
                (element_key, selector, sel_type, confidence, now),
            )
            self._conn.commit()
            return c.lastrowid

    def get_selectors(self, element_key: str) -> List[Dict]:
        with self._lock:
            c = self._conn.cursor()
            c.execute(
                "SELECT * FROM selectors WHERE element_key=? ORDER BY success_count DESC, confidence DESC, last_seen DESC",
                (element_key,),
            )
            rows = c.fetchall()
            return [dict(r) for r in rows]

    def record_success(self, selector: str):
        with self._lock:
            c = self._conn.cursor()
            now = time.time()
            c.execute(
                "UPDATE selectors SET success_count = success_count + 1, last_seen = ? WHERE selector = ?",
                (now, selector),
            )
            self._conn.commit()
            # gently increase confidence for selectors that succeed
            try:
                c.execute("SELECT confidence FROM selectors WHERE selector = ?", (selector,))
                row = c.fetchone()
                if row:
                    conf = float(row[0])
                    conf = min(1.0, conf + 0.05)
                    c.execute("UPDATE selectors SET confidence = ? WHERE selector = ?", (conf, selector))
                    self._conn.commit()
            except Exception:
                pass

    def record_failure(self, selector: str):
        with self._lock:
            c = self._conn.cursor()
            c.execute(
                "UPDATE selectors SET failure_count = failure_count + 1 WHERE selector = ?",
                (selector,),
            )
            self._conn.commit()
            # gently decrease confidence on failures
            try:
                c.execute("SELECT confidence FROM selectors WHERE selector = ?", (selector,))
                row = c.fetchone()
                if row:
                    conf = float(row[0])
                    conf = max(0.0, conf - 0.08)
                    c.execute("UPDATE selectors SET confidence = ? WHERE selector = ?", (conf, selector))
                    self._conn.commit()
            except Exception:
                pass

    def prune_selectors(self, max_age_days: int = 90, min_success: int = 1):
        """Remove selectors that are too old and have low success counts.

        This helps keep the selector store focused and prevents stale selectors
        from polluting the healing process.
        """
        cutoff = time.time() - (max_age_days * 24 * 3600)
        with self._lock:
            c = self._conn.cursor()
            c.execute(
                "DELETE FROM selectors WHERE (last_seen IS NULL OR last_seen < ?) AND success_count <= ?",
                (cutoff, min_success),
            )
            self._conn.commit()

    def record_healed_event(self, step: str, element_key: str, old_selector: str, new_selector: str):
        with self._lock:
            c = self._conn.cursor()
            ts = time.time()
            c.execute(
                "INSERT INTO healed_events (timestamp, step, element_key, old_selector, new_selector) VALUES (?,?,?,?,?)",
                (ts, step, element_key, old_selector, new_selector),
            )
            self._conn.commit()

    def get_healed_events(self, since: Optional[float] = None) -> List[Dict]:
        with self._lock:
            c = self._conn.cursor()
            if since:
                c.execute("SELECT * FROM healed_events WHERE timestamp >= ? ORDER BY timestamp DESC", (since,))
            else:
                c.execute("SELECT * FROM healed_events ORDER BY timestamp DESC")
            rows = c.fetchall()
            return [dict(r) for r in rows]

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass
