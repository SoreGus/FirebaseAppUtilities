from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta, timezone
from statistics import mean
from typing import Any

from google.cloud.firestore_v1 import Client

from ..cache import LocalStore


class AnalyticsService:
    """Cost-aware analytics backed by Firestore and a persistent local cache."""

    def __init__(
        self,
        client: Client,
        store: LocalStore,
        collection: str = "analytics_events",
    ):
        self._client = client
        self._store = store
        self.collection = collection


    def list_events(
        self,
        *,
        event_name: str | None = None,
        days: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Explicit remote document query kept for CLI/programmatic use."""
        query = self._base_query(event_name=event_name, days=days).order_by(
            "timestamp", direction="DESCENDING"
        ).limit(max(1, limit))
        return [
            {"id": snapshot.id, **(snapshot.to_dict() or {})}
            for snapshot in query.stream()
        ]

    def count_by_name(
        self,
        *,
        days: int | None = None,
        limit: int = 5000,
    ) -> dict[str, int]:
        """Compatibility helper for explicit CLI use; scans up to ``limit`` events."""
        counter: Counter[str] = Counter()
        for event in self.list_events(days=days, limit=limit):
            name = event.get("name")
            if isinstance(name, str) and name:
                counter[name] += 1
        return dict(counter.most_common())

    def count_events(
        self,
        *,
        event_name: str | None = None,
        days: int | None = None,
        property_filters: dict[str, Any] | None = None,
    ) -> int:
        """Run a Firestore COUNT aggregation without downloading matching documents."""
        query = self._base_query(event_name=event_name, days=days, property_filters=property_filters)
        result = query.count().get()
        if not result:
            return 0
        first = result[0]
        if isinstance(first, (list, tuple)) and first:
            first = first[0]
        value = getattr(first, "value", first)
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def sync_events(
        self,
        *,
        event_name: str,
        days: int | None = 30,
        limit: int = 1000,
        property_filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Fetch only events newer than the local cursor for one event type."""
        filter_key = ";".join(
            f"{key}={property_filters[key]}" for key in sorted(property_filters or {})
        )
        sync_key = f"analytics:{self.collection}:{event_name}:{days}:{filter_key}"
        state = self._store.sync_state(sync_key)
        cursor = state.get("last_timestamp") if state else None
        requested_since = self._since(days) if days is not None else None
        lower_bound = max(
            [value for value in (cursor, requested_since) if value is not None],
            default=None,
        )

        query = self._client.collection(self.collection).where(
            filter=self._field_filter("name", "==", event_name)
        )
        for key, value in (property_filters or {}).items():
            query = query.where(
                filter=self._field_filter(f"properties.{key}", "==", value)
            )
        if lower_bound is not None:
            query = query.where(
                filter=self._field_filter("timestamp", ">", lower_bound)
            )
        query = query.order_by("timestamp", direction="ASCENDING").limit(max(1, limit))

        snapshots = list(query.stream())
        documents = [{"id": item.id, **(item.to_dict() or {})} for item in snapshots]
        self._store.upsert_documents(
            self.collection,
            documents,
            timestamp_field="timestamp",
        )

        newest = cursor
        for document in documents:
            timestamp = self._as_datetime(document.get("timestamp"))
            if timestamp is not None and (newest is None or timestamp > newest):
                newest = timestamp
        self._store.set_sync_state(sync_key, newest)

        return {
            "fetched": len(documents),
            "has_more": len(documents) >= max(1, limit),
            "last_timestamp": newest,
            "synced_at": datetime.now(timezone.utc),
        }

    def local_events(
        self,
        *,
        event_name: str | None = None,
        days: int | None = None,
        limit: int | None = 100,
        property_filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        documents = self._store.query_documents(
            self.collection,
            event_name=event_name,
            since=self._since(days) if days is not None else None,
            limit=None if property_filters else limit,
        )
        if property_filters:
            documents = [
                document for document in documents
                if self._matches_properties(document, property_filters)
            ]
            if limit is not None:
                documents = documents[:limit]
        return documents

    def local_count(
        self,
        *,
        event_name: str | None = None,
        days: int | None = None,
        property_filters: dict[str, Any] | None = None,
    ) -> int:
        if property_filters:
            return len(
                self.local_events(
                    event_name=event_name,
                    days=days,
                    limit=None,
                    property_filters=property_filters,
                )
            )
        return self._store.count_documents(
            self.collection,
            event_name=event_name,
            since=self._since(days) if days is not None else None,
        )

    def local_property_counts(
        self,
        property_key: str,
        *,
        event_name: str,
        days: int | None = None,
        top: int = 20,
        property_filters: dict[str, Any] | None = None,
    ) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for event in self.local_events(
            event_name=event_name,
            days=days,
            limit=None,
            property_filters=property_filters,
        ):
            properties = event.get("properties")
            if not isinstance(properties, dict):
                continue
            value = properties.get(property_key)
            if value is not None:
                counter[str(value)] += 1
        return dict(counter.most_common(top))

    def local_average(
        self,
        property_key: str,
        *,
        event_name: str,
        days: int | None = None,
        property_filters: dict[str, Any] | None = None,
    ) -> float | None:
        values: list[float] = []
        for event in self.local_events(
            event_name=event_name,
            days=days,
            limit=None,
            property_filters=property_filters,
        ):
            properties = event.get("properties")
            if not isinstance(properties, dict):
                continue
            value = properties.get(property_key)
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                values.append(float(value))
        return mean(values) if values else None

    def local_activity_by_day(
        self,
        *,
        event_name: str | None = None,
        days: int | None = 30,
        property_filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        events = self.local_events(
            event_name=event_name,
            days=days,
            limit=None,
            property_filters=property_filters,
        )
        counts: Counter[date] = Counter()
        for event in events:
            value = self._as_datetime(event.get("timestamp"))
            if value is not None:
                counts[value.date()] += 1

        if days is None:
            ordered = sorted(counts)
        else:
            today = datetime.now(timezone.utc).date()
            first = today - timedelta(days=max(days - 1, 0))
            ordered = [first + timedelta(days=offset) for offset in range(days)]
        return [{"date": day.isoformat(), "count": counts.get(day, 0)} for day in ordered]

    def last_sync(
        self,
        *,
        event_name: str,
        days: int | None = 30,
        property_filters: dict[str, Any] | None = None,
    ) -> datetime | None:
        filter_key = ";".join(
            f"{key}={property_filters[key]}" for key in sorted(property_filters or {})
        )
        state = self._store.sync_state(
            f"analytics:{self.collection}:{event_name}:{days}:{filter_key}"
        )
        return state.get("synced_at") if state else None

    def _base_query(
        self,
        *,
        event_name: str | None,
        days: int | None,
        property_filters: dict[str, Any] | None = None,
    ):
        query = self._client.collection(self.collection)
        if event_name:
            query = query.where(filter=self._field_filter("name", "==", event_name))
        if days is not None:
            query = query.where(filter=self._field_filter("timestamp", ">=", self._since(days)))
        for key, value in (property_filters or {}).items():
            query = query.where(
                filter=self._field_filter(f"properties.{key}", "==", value)
            )
        return query

    @staticmethod
    def _matches_properties(document: dict[str, Any], filters: dict[str, Any]) -> bool:
        properties = document.get("properties")
        if not isinstance(properties, dict):
            return False
        return all(properties.get(key) == value for key, value in filters.items())

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
