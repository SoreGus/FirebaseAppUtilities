from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Any, Iterable


class LocalStore:
    """Small persistent SQLite cache for immutable Firestore documents."""

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    collection TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    timestamp TEXT,
                    event_name TEXT,
                    category TEXT,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (collection, document_id)
                );

                CREATE INDEX IF NOT EXISTS idx_documents_collection_timestamp
                ON documents(collection, timestamp DESC);

                CREATE INDEX IF NOT EXISTS idx_documents_collection_event_timestamp
                ON documents(collection, event_name, timestamp DESC);

                CREATE INDEX IF NOT EXISTS idx_documents_collection_category_timestamp
                ON documents(collection, category, timestamp DESC);

                CREATE TABLE IF NOT EXISTS sync_state (
                    sync_key TEXT PRIMARY KEY,
                    last_timestamp TEXT,
                    synced_at TEXT NOT NULL
                );
                """
            )

    def upsert_documents(
        self,
        collection: str,
        documents: Iterable[dict[str, Any]],
        *,
        timestamp_field: str,
    ) -> int:
        rows: list[tuple[str, str, str | None, str | None, str | None, str]] = []
        for document in documents:
            document_id = str(document.get("id", "")).strip()
            if not document_id:
                continue
            timestamp = self._serialize_timestamp(document.get(timestamp_field))
            rows.append(
                (
                    collection,
                    document_id,
                    timestamp,
                    self._string_or_none(document.get("name")),
                    self._string_or_none(document.get("category")),
                    json.dumps(document, default=self._json_default, ensure_ascii=False),
                )
            )

        if not rows:
            return 0

        with self._lock, self._connect() as connection:
            before = connection.total_changes
            connection.executemany(
                """
                INSERT INTO documents(
                    collection, document_id, timestamp, event_name, category, payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(collection, document_id) DO UPDATE SET
                    timestamp=excluded.timestamp,
                    event_name=excluded.event_name,
                    category=excluded.category,
                    payload=excluded.payload
                """,
                rows,
            )
            return connection.total_changes - before

    def query_documents(
        self,
        collection: str,
        *,
        event_name: str | None = None,
        category: str | None = None,
        since: datetime | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        clauses = ["collection = ?"]
        values: list[Any] = [collection]

        if event_name is not None:
            clauses.append("event_name = ?")
            values.append(event_name)
        if category is not None:
            clauses.append("category = ?")
            values.append(category)
        if since is not None:
            clauses.append("timestamp >= ?")
            values.append(self._serialize_timestamp(since))

        sql = (
            "SELECT payload FROM documents WHERE "
            + " AND ".join(clauses)
            + " ORDER BY timestamp DESC, document_id DESC"
        )
        if limit is not None:
            sql += " LIMIT ?"
            values.append(max(1, int(limit)))

        with self._lock, self._connect() as connection:
            rows = connection.execute(sql, values).fetchall()

        return [self._decode_payload(row["payload"]) for row in rows]

    def count_documents(
        self,
        collection: str,
        *,
        event_name: str | None = None,
        category: str | None = None,
        since: datetime | None = None,
    ) -> int:
        clauses = ["collection = ?"]
        values: list[Any] = [collection]
        if event_name is not None:
            clauses.append("event_name = ?")
            values.append(event_name)
        if category is not None:
            clauses.append("category = ?")
            values.append(category)
        if since is not None:
            clauses.append("timestamp >= ?")
            values.append(self._serialize_timestamp(since))

        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM documents WHERE " + " AND ".join(clauses),
                values,
            ).fetchone()
        return int(row["count"] if row else 0)

    def newest_timestamp(
        self,
        collection: str,
        *,
        event_name: str | None = None,
    ) -> datetime | None:
        clauses = ["collection = ?", "timestamp IS NOT NULL"]
        values: list[Any] = [collection]
        if event_name is not None:
            clauses.append("event_name = ?")
            values.append(event_name)

        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT MAX(timestamp) AS value FROM documents WHERE " + " AND ".join(clauses),
                values,
            ).fetchone()
        return self._parse_timestamp(row["value"] if row else None)

    def set_sync_state(self, sync_key: str, last_timestamp: datetime | None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sync_state(sync_key, last_timestamp, synced_at)
                VALUES (?, ?, ?)
                ON CONFLICT(sync_key) DO UPDATE SET
                    last_timestamp=excluded.last_timestamp,
                    synced_at=excluded.synced_at
                """,
                (sync_key, self._serialize_timestamp(last_timestamp), now),
            )

    def sync_state(self, sync_key: str) -> dict[str, datetime | None] | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT last_timestamp, synced_at FROM sync_state WHERE sync_key = ?",
                (sync_key,),
            ).fetchone()
        if row is None:
            return None
        return {
            "last_timestamp": self._parse_timestamp(row["last_timestamp"]),
            "synced_at": self._parse_timestamp(row["synced_at"]),
        }

    @staticmethod
    def _string_or_none(value: Any) -> str | None:
        return value if isinstance(value, str) and value else None

    @staticmethod
    def _serialize_timestamp(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).isoformat()
        if isinstance(value, str):
            parsed = LocalStore._parse_timestamp(value)
            return parsed.astimezone(timezone.utc).isoformat() if parsed else value
        return None

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    @staticmethod
    def _json_default(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _decode_payload(payload: str) -> dict[str, Any]:
        value = json.loads(payload)
        return value if isinstance(value, dict) else {}
