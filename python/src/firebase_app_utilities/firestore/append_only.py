from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from google.cloud.firestore_v1 import Client

from ..cache import LocalStore


class AppendOnlyCollectionService:
    """Incremental sync for immutable/append-only Firestore collections."""

    def __init__(self, client: Client, store: LocalStore):
        self._client = client
        self._store = store

    def sync(
        self,
        collection: str,
        *,
        timestamp_field: str,
        days: int | None = None,
        limit: int = 500,
        filters: tuple[tuple[str, str, Any], ...] = (),
        sync_key: str | None = None,
    ) -> dict[str, Any]:
        key = sync_key or self._sync_key(collection, timestamp_field, filters, days)
        state = self._store.sync_state(key)
        cursor = state.get("last_timestamp") if state else None
        requested_since = self._since(days) if days is not None else None
        lower_bound = max(
            [value for value in (cursor, requested_since) if value is not None],
            default=None,
        )

        query = self._client.collection(collection)
        for field, operator, value in filters:
            query = query.where(filter=self._field_filter(field, operator, value))
        if lower_bound is not None:
            query = query.where(
                filter=self._field_filter(timestamp_field, ">", lower_bound)
            )
        query = query.order_by(timestamp_field, direction="ASCENDING").limit(max(1, limit))

        snapshots = list(query.stream())
        documents = [{"id": item.id, **(item.to_dict() or {})} for item in snapshots]
        self._store.upsert_documents(
            collection,
            documents,
            timestamp_field=timestamp_field,
        )

        newest = cursor
        for document in documents:
            value = self._as_datetime(document.get(timestamp_field))
            if value is not None and (newest is None or value > newest):
                newest = value

        self._store.set_sync_state(key, newest)
        return {
            "fetched": len(documents),
            "has_more": len(documents) >= max(1, limit),
            "last_timestamp": newest,
            "synced_at": datetime.now(timezone.utc),
        }

    def local_documents(
        self,
        collection: str,
        *,
        days: int | None = None,
        category: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return self._store.query_documents(
            collection,
            category=category,
            since=self._since(days) if days is not None else None,
            limit=limit,
        )

    def local_count(
        self,
        collection: str,
        *,
        days: int | None = None,
        category: str | None = None,
    ) -> int:
        return self._store.count_documents(
            collection,
            category=category,
            since=self._since(days) if days is not None else None,
        )

    @staticmethod
    def _sync_key(
        collection: str,
        timestamp_field: str,
        filters: tuple[tuple[str, str, Any], ...],
        days: int | None,
    ) -> str:
        serialized_filters = ";".join(f"{field}{op}{value}" for field, op, value in filters)
        return f"append:{collection}:{timestamp_field}:{days}:{serialized_filters}"

    @staticmethod
    def _since(days: int) -> datetime:
        return datetime.now(timezone.utc) - timedelta(days=max(0, days))

    @staticmethod
    def _as_datetime(value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                return None
        return None

    @staticmethod
    def _field_filter(field: str, operator: str, value: Any) -> Any:
        from google.cloud.firestore_v1.base_query import FieldFilter

        return FieldFilter(field, operator, value)
