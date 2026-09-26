from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any

from google.cloud.firestore_v1 import Client


class AnalyticsService:
    """Reusable analytics queries backed by a Firestore collection."""

    def __init__(
        self,
        client: Client,
        collection: str = "analytics_events",
    ):
        self._client = client
        self.collection = collection

    def list_events(
        self,
        *,
        event_name: str | None = None,
        days: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        query = self._client.collection(self.collection)

        if event_name:
            query = query.where(
                filter=self._field_filter(
                    "name",
                    "==",
                    event_name,
                )
            )

        if days is not None:
            query = query.where(
                filter=self._field_filter(
                    "timestamp",
                    ">=",
                    self._since(days),
                )
            )

        query = query.order_by(
            "timestamp",
            direction="DESCENDING",
        ).limit(limit)

        return [
            {
                "id": snapshot.id,
                **(snapshot.to_dict() or {}),
            }
            for snapshot in query.stream()
        ]

    def overview(
        self,
        *,
        days: int | None = None,
        limit: int = 5000,
    ) -> dict[str, Any]:
        events = self._events_for_aggregation(days=days, limit=limit)
        names: Counter[str] = Counter()
        users: set[str] = set()
        sessions: set[str] = set()

        for event in events:
            name = event.get("name")
            user = event.get("userId")
            session = event.get("sessionId")

            if isinstance(name, str) and name:
                names[name] += 1

            if isinstance(user, str) and user:
                users.add(user)

            if isinstance(session, str) and session:
                sessions.add(session)

        return {
            "total_events": len(events),
            "unique_users": len(users),
            "unique_sessions": len(sessions),
            "events": dict(names.most_common()),
        }

    def count_by_name(
        self,
        *,
        days: int | None = None,
        limit: int = 5000,
    ) -> dict[str, int]:
        return self.overview(days=days, limit=limit)["events"]

    def total_events(
        self,
        *,
        days: int | None = None,
        limit: int = 5000,
    ) -> int:
        return int(self.overview(days=days, limit=limit)["total_events"])

    def unique_users(
        self,
        *,
        days: int | None = None,
        limit: int = 5000,
    ) -> int:
        return int(self.overview(days=days, limit=limit)["unique_users"])

    def unique_sessions(
        self,
        *,
        days: int | None = None,
        limit: int = 5000,
    ) -> int:
        return int(self.overview(days=days, limit=limit)["unique_sessions"])

    def property_counts(
        self,
        property_key: str,
        *,
        event_name: str | None = None,
        days: int | None = None,
        limit: int = 5000,
        top: int = 20,
    ) -> dict[str, int]:
        counter: Counter[str] = Counter()

        for event in self._events_for_aggregation(days=days, limit=limit):
            if event_name and event.get("name") != event_name:
                continue

            properties = event.get("properties")

            if not isinstance(properties, dict):
                continue

            value = properties.get(property_key)

            if value is None:
                continue

            counter[str(value)] += 1

        return dict(counter.most_common(top))

    def activity_by_day(
        self,
        *,
        days: int | None = 30,
        limit: int = 5000,
    ) -> list[dict[str, Any]]:
        events = self._events_for_aggregation(days=days, limit=limit)
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

        return [
            {
                "date": day.isoformat(),
                "count": counts.get(day, 0),
            }
            for day in ordered
        ]

    def event_names(
        self,
        *,
        days: int | None = None,
        limit: int = 5000,
    ) -> list[str]:
        return list(self.count_by_name(days=days, limit=limit).keys())

    def dashboard_snapshot(
        self,
        *,
        days: int | None = 30,
        recent_limit: int = 25,
        aggregation_limit: int = 5000,
    ) -> dict[str, Any]:
        return {
            "overview": self.overview(days=days, limit=aggregation_limit),
            "activity": self.activity_by_day(days=days, limit=aggregation_limit),
            "recent_events": self.list_events(days=days, limit=recent_limit),
        }

    def _events_for_aggregation(
        self,
        *,
        days: int | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        query = self._client.collection(self.collection)

        if days is not None:
            query = query.where(
                filter=self._field_filter(
                    "timestamp",
                    ">=",
                    self._since(days),
                )
            )

        query = query.limit(limit)

        return [
            snapshot.to_dict() or {}
            for snapshot in query.stream()
        ]

    @staticmethod
    def _since(days: int) -> datetime:
        return datetime.now(timezone.utc) - timedelta(days=days)

    @staticmethod
    def _as_datetime(value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None

        return None

    @staticmethod
    def _field_filter(field: str, operator: str, value: Any) -> Any:
        from google.cloud.firestore_v1.base_query import FieldFilter

        return FieldFilter(field, operator, value)
